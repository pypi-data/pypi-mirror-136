import logging
import os
import socket
import struct
import tempfile
import time
import warnings
from collections import OrderedDict
from select import select

import jinja2
import numpy as np
from nengo.exceptions import SimulationError

from nengo_loihi.builder.discretize import scale_pes_errors
from nengo_loihi.hardware.allocators import GreedyInterchip
from nengo_loihi.hardware.builder import build_board
from nengo_loihi.hardware.nxsdk_objects import LoihiSpikeInput
from nengo_loihi.hardware.nxsdk_shim import (
    SnipPhase,
    SpikeProbe,
    assert_nxsdk,
    nxsdk,
    parse_nxsdk_version,
)
from nengo_loihi.hardware.validate import validate_board
from nengo_loihi.probe import LoihiProbe, ProbeFilter

logger = logging.getLogger(__name__)


def ceil_div(a, b):
    return -((-a) // b)


def roundup(a, b):
    return b * ceil_div(a, b)


class HardwareInterface:
    """Place a Model onto a Loihi board and run it.

    Parameters
    ----------
    model : Model
        Model specification that will be placed on the Loihi board.
    use_snips : boolean, optional (Default: True)
        Whether to use snips (e.g., for ``precompute=False``).
    seed : int, optional (Default: None)
        A seed for stochastic operations.
    snip_max_spikes_per_step : int
        The maximum number of spikes that can be sent to each chip in one
        timestep if ``.use_snips`` is True.
    n_chips : int, optional (Default: 2)
        The number of chips on the board.
    allocator : Allocator, optional (Default: ``GreedyInterchip()``)
        Callable object that allocates the board's devices to given models.
        Defaults to one block and one input per core on a single chip.
    """

    connection_retries = 3
    min_nxsdk_version = parse_nxsdk_version("0.9.0")
    max_nxsdk_version = parse_nxsdk_version("1.0.0")

    def __init__(
        self,
        model,
        use_snips=True,
        seed=None,
        snip_max_spikes_per_step=50,
        n_chips=2,
        allocator=None,
    ):
        self.closed = False

        self.model = model
        self.use_snips = use_snips
        self.seed = seed
        self._probe_filter = ProbeFilter(dt=self.model.dt)

        self.check_nxsdk_version()

        # clear cached content from SpikeProbe class attribute
        SpikeProbe.probeDict.clear()

        # --- allocate
        allocator = GreedyInterchip() if allocator is None else allocator
        self.board = allocator(self.model, n_chips=n_chips)

        # --- validate
        validate_board(self.board)

        # --- build
        self.nxsdk_board = build_board(
            self.board, use_snips=self.use_snips, seed=self.seed
        )

        # --- create snips or non-snip infrastructure
        self.snips, self.no_snips = None, None
        if self.use_snips:
            self.snips = Snips(
                self.model, self.board, self.nxsdk_board, snip_max_spikes_per_step
            )
            self.chip2host = self.snips.chip2host

        else:
            self.no_snips = NoSnips(
                self.model.dt,
                self.board.probe_map,
                self.nxsdk_board.global_spike_generator,
            )
            self.chip2host = self.no_snips.chip2host

    def __enter__(self):
        if self.closed:
            raise SimulationError(
                "Loihi interface has been closed and cannot be reopened."
            )

        if not self.connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @classmethod
    def check_nxsdk_version(cls):
        # raise exception if nxsdk not installed
        assert_nxsdk()

        # if installed, check version (parse it here so that monkeypatch tests work)
        nxsdk_version = parse_nxsdk_version(nxsdk)
        if nxsdk_version < cls.min_nxsdk_version:
            raise ImportError(
                "nengo-loihi requires nxsdk>=%s, found %s"
                % (cls.min_nxsdk_version, nxsdk_version)
            )
        elif nxsdk_version > cls.max_nxsdk_version:
            warnings.warn(
                "nengo-loihi has not been tested with your nxsdk "
                "version (%s); latest fully supported version is "
                "%s" % (nxsdk_version, cls.max_nxsdk_version)
            )

    @property
    def connected(self):
        return self.nxsdk_board is not None and self.nxsdk_board.executor.hasStarted()

    def clear_probes(self):
        # Probe data in `self.probes` is cleared after it is retrieved by a
        # `self.collect_probe_output` call, so nothing needs to happen here.
        # This function remains so that `nengo_loihi.Simulator` can call `clear_probes`
        # on all of its internal simulators without checking their types.
        pass

    def close(self):
        if self.snips is not None and self.snips.connected:
            self.snips.close()

        if self.nxsdk_board is not None:
            self.nxsdk_board.disconnect()
            self.nxsdk_board = None

        self.closed = True

    def collect_probe_output(self, probe):
        """Get and clear output from a particular probe"""
        assert isinstance(probe, LoihiProbe)
        communicator = self.snips if self.use_snips else self.no_snips
        out = communicator.collect_probe_output(probe)
        return self._probe_filter(probe, out)

    def connect(self):
        """Connects to the board."""

        logger.info("Connecting to Loihi, max attempts: %d", self.connection_retries)
        last_exception = None
        for i in range(self.connection_retries):
            try:
                self.nxsdk_board.start()
                if self.connected:
                    break
            except Exception as e:
                last_exception = e
                logger.warning("Connection error: %s", e)
                time.sleep(1)
                logger.info("Retrying, attempt %d", i + 1)
        else:
            raise SimulationError(
                "Board connection error%s"
                % (": %s" % last_exception if last_exception is not None else "")
            )

    def host2chip(self, spikes, errors):
        loihi_spikes = OrderedDict()
        for spike_input, t, s in spikes:
            loihi_spike_input = self.nxsdk_board.spike_inputs[spike_input]
            loihi_spikes.setdefault(t, []).extend(loihi_spike_input.spikes_to_loihi(s))

        if self.use_snips:
            if len(loihi_spikes) > 0:
                assert len(loihi_spikes) == 1, "Snips process one timestep at a time"
                loihi_spikes = next(iter(loihi_spikes.values()))
                loihi_spikes = np.hstack(loihi_spikes) if len(loihi_spikes) > 0 else []
            else:
                loihi_spikes = []
            return self.snips.host2chip(loihi_spikes, errors)
        else:
            assert (
                len(errors) == 0
            ), "Learning only supported with snips (`precompute=False`)"
            return self.no_snips.host2chip(loihi_spikes)

    def run_steps(self, steps, blocking=True):
        assert self.connected, "Interface is not built"

        # start the board running the desired number of steps
        self.nxsdk_board.run(steps, aSync=not blocking)

        # connect snips
        if self.use_snips and not self.snips.connected:
            self.snips.connect(self.nxsdk_board)

    def wait_for_completion(self):
        self.nxsdk_board.finishRun()


class NoSnips:
    def __init__(self, dt, probe_map, spike_generator):
        self.step = 0

        self.dt = dt
        self.probe_map = probe_map
        self.spike_generator = spike_generator

    def clear_probe(self, probe):
        nxsdk_probes = self.probe_map[probe]
        for nxsdk_probe in nxsdk_probes:
            for p in nxsdk_probe:
                data = p.timeSeries.data
                data.clear()

    def collect_probe_output(self, probe):
        nxsdk_probes = self.probe_map[probe]
        outputs = [
            np.column_stack([p.timeSeries.data for p in nxsdk_probe])
            for nxsdk_probe in nxsdk_probes
        ]
        self.clear_probe(probe)

        if len(outputs) > 0:
            outputs = probe.weight_outputs(outputs)

        return outputs

    def chip2host(self, probes_receivers):
        increment = None
        for probe, receiver in probes_receivers.items():
            outputs = self.collect_probe_output(probe)

            if len(outputs) > 0:
                if increment is None:
                    increment = len(outputs)

                assert increment == len(
                    outputs
                ), "All outputs need same number of steps"

                for j in range(len(outputs)):
                    receiver.receive(self.dt * (self.step + j + 2), outputs[j])

        if increment is not None:
            self.step += increment

    def host2chip(self, loihi_spikes):
        nxsdk_spike_generator = self.spike_generator
        tmax = -1
        for t, spikes in loihi_spikes.items():
            assert t >= tmax, "Spikes must be in order"
            tmax = t
            LoihiSpikeInput.add_spikes_to_generator(t, spikes, nxsdk_spike_generator)


class Snips:

    channel_packet_elements = 64  # size of channel packets in int32s
    channel_bytes_per_element = 4  # bytes per int32 (channel packets element size)
    packet_bytes = channel_packet_elements * channel_bytes_per_element
    error_info_size = 2  # size of returned error info (other sizes not implemented)

    snips_dir = os.path.join(os.path.dirname(__file__), "snips")
    env = jinja2.Environment(
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(snips_dir),
        keep_trailing_newline=True,
    )

    def __init__(self, model, board, nxsdk_board, max_spikes_per_step):
        self.max_spikes_per_step = max_spikes_per_step
        self.model = model

        self.error_chip_map = {}  # maps synapses to core/chip locations for errors
        self.probe_data = OrderedDict()
        self.tmp_snip_dir = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        self.host_snip = HostSnip(self.tmp_snip_dir.name)
        self.chip_snips = []
        # Map from probe to information to get outputs of that probe. Each tuple has:
        # - chip_idx: the index of a chip to get information from
        # - output_slice: a slice of outputs for the probe
        # - n_packed_spikes: the number of spikes that have been "packed" to a dense
        #   storage format (if 0, the spikes have not been packed).
        # There will be at least one entry per chip that the probe gets output from,
        # and possibly more if the outputs cannot be represented with one slice.
        self.snip_range = {}

        for idx, chip in enumerate(board.chips):
            self.chip_snips.append(ChipSnips(idx, chip, self.tmp_snip_dir.name))
            for core in chip.cores:
                if core.learning_coreid is None:
                    continue
                for synapse in core.blocks[0].synapses:
                    self.error_chip_map[synapse] = (idx, core.learning_coreid)

        for probe in model.probes:
            self.probe_data[probe] = []
            pinfo = board.probe_map[probe]
            for target_idx, block in enumerate(probe.target):
                chip_idx = pinfo.chip_idx[target_idx]
                self.chip_snips[chip_idx].prepare_for_probe(block, pinfo, target_idx)
            self.snip_range[probe] = pinfo.snip_range

        for chip_snip in self.chip_snips:
            chip_snip.create(nxsdk_board, self.max_spikes_per_step)

        self.host_snip.create(nxsdk_board, self.chip_snips)

        for chip_snip in self.chip_snips:
            chip_snip.input_channel.connect(self.host_snip.snip, chip_snip.io_snip)
            chip_snip.output_channel.connect(chip_snip.io_snip, self.host_snip.snip)

        self.bytes_per_step = self.packet_bytes * sum(
            chip_snip.n_output_packets for chip_snip in self.chip_snips
        )

    @classmethod
    def render_template(cls, template, path, **template_data):
        template = cls.env.get_template("{}.template".format(template))
        code = template.render(error_info_size=cls.error_info_size, **template_data)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

    @property
    def connected(self):
        return self.host_snip is not None and self.host_snip.connected

    def clear_probe(self, probe):
        self.probe_data[probe].clear()

    def close(self):
        if self.host_snip is not None:
            self.host_snip.close()

    def collect_probe_output(self, probe):
        out = list(self.probe_data[probe])
        self.clear_probe(probe)
        return out

    def connect(self, nxsdk_board):
        if self.host_snip is not None:
            self.host_snip.connect(nxsdk_board)

    def chip2host(self, probes_receivers):
        assert self.host_snip.connected

        raw_data = self.host_snip.recv_bytes(self.bytes_per_step)

        # create views into data for different chips
        time_steps = []
        chip_data = []
        i = 0

        for chip_snip in self.chip_snips:
            data = raw_data[i : i + chip_snip.n_outputs]
            assert len(data) == chip_snip.n_outputs
            assert chip_snip.n_outputs > 0, "Chip should always send timestep"
            time_steps.append(data[0])
            chip_data.append(data[1:])
            i += Snips.channel_packet_elements * chip_snip.n_output_packets

        assert all(ts == time_steps[0] for ts in time_steps), "Chips are out of sync!"

        for probe in self.probe_data:
            outputs = []
            for chip_idx, data_slice, n_packed_spikes in self.snip_range[probe]:
                data = chip_data[chip_idx][data_slice]
                if n_packed_spikes > 0:
                    packed8 = data.view("uint8")
                    unpacked = np.unpackbits(packed8)
                    unpacked = unpacked.reshape((-1, 8))[:, ::-1].ravel()
                    unpacked = unpacked[:n_packed_spikes]
                    outputs.append(unpacked)
                else:
                    outputs.append(data)

            assert all(x.ndim == 1 for x in outputs)
            weighted_outputs = probe.weight_outputs(outputs)[0]

            receiver = probes_receivers.get(probe, None)
            if receiver is not None:
                # chip->host
                receiver.receive(self.model.dt * time_steps[chip_idx], weighted_outputs)
            else:
                # onchip probes
                self.probe_data[probe].append(weighted_outputs)

    def host2chip(self, loihi_spikes, errors):
        assert self.host_snip.connected

        error_info = [[] for _ in self.chip_snips]
        error_vecs = [[] for _ in self.chip_snips]
        for synapse, t, e in errors:
            chip_idx, core_id = self.error_chip_map[synapse]
            error_info[chip_idx].append([core_id, len(e)])
            error_vecs[chip_idx].append(e)

        # First `n_chips` elements of `msg` record number of elements going to
        # each chip. We fill these once we create the message and can measure length.
        data = [None for _ in self.chip_snips]
        for chip_snip in self.chip_snips:
            # measure current msg length to see how much it grows
            data_len0 = len(data)

            chip_spikes = (
                loihi_spikes[loihi_spikes["chip_id"] == chip_snip.chip_id]
                if len(loihi_spikes) > 0
                else []
            )

            max_spikes = self.max_spikes_per_step
            if len(chip_spikes) > max_spikes:
                warnings.warn(
                    "Too many spikes (%d) sent in one timestep. Increase the "
                    "value of `snip_max_spikes_per_step` (currently set to %d). "
                    "See\n  https://www.nengo.ai/nengo-loihi/configuration.html\n"
                    "for details." % (len(chip_spikes), max_spikes)
                )
                chip_spikes = chip_spikes[:max_spikes]

            data.append(len(chip_spikes))
            data.extend(SpikePacker.pack(chip_spikes))

            if len(error_vecs[chip_snip.idx]) != 0:
                error_vecs_i = np.concatenate(error_vecs[chip_snip.idx])
                error_vecs_i = scale_pes_errors(
                    error_vecs_i, scale=self.model.pes_error_scale
                )

                assert len(error_info[chip_snip.idx]) == chip_snip.n_errors
                i = 0
                for core_id, e_len in error_info[chip_snip.idx]:
                    data.extend([core_id, e_len] + error_vecs_i[i : i + e_len].tolist())
                    i += e_len

            data[chip_snip.idx] = len(data) - data_len0

        self.host_snip.send_all(data)


class ChipSnips:
    """Track information for creating Snips for each chip.

    Attributes
    ----------
    chip_id : int
        ID of the chip.
    cores : set
        Core IDs with output.
    idx : int
        Index of the chip.
    input_channel
        The channel used to provide input to the chip.
    io_snip
        The IO snip process associated with this chip.
    last_output : int
        The last output processed. Used to fill out ``snip_range`` correctly.
    learn_snip
        The learn snip process associated with this chip.
    n_errors : int
        The number of cores receiving learning errors.
    n_output_packets : int
        Number of packets required to send all outputs.
    n_outputs : int
        Total number of outputs, in int32s.
    output_channel
        The channel used to gather output from the chip.
    probes : list of tuples
        Each tuple is ``(offset, key, core_id, comp_start, comp_step, comp_len)``
    total_error_length : int
        The total length of error information, in int32s.
    """

    output_header_len = 1  # First output is timestamp
    output_offset = output_header_len

    def __init__(self, idx, chip, tmp_snip_dir):
        self.idx = idx
        self.tmp_snip_dir = tmp_snip_dir

        # --- determine required information for learning
        self.n_errors = 0
        self.total_error_len = 0
        for core in chip.cores:
            if core.learning_coreid is None:
                continue

            assert (
                len(core.blocks) == 1
            ), "Learning not implemented with multiple blocks per core"
            self.n_errors += 1
            self.total_error_len += 2 + core.blocks[0].n_neurons // 2

        self.cores = set()
        self.probes = []
        self.io_snip = None
        self.learn_snip = None
        self.chip_id = None
        self.input_channel = None
        self.output_channel = None
        self.last_output = 0

    @property
    def input_channel_name(self):
        return "nengo_io_h2c_chip_%d" % self.idx

    @property
    def last_output(self):
        return self._last_output

    @last_output.setter
    def last_output(self, val):
        self._last_output = val
        # number of outputs (in ints and packets) for each chip
        self._n_outputs = self.output_offset + val
        self._n_output_packets = ceil_div(
            self._n_outputs, Snips.channel_packet_elements
        )

    @property
    def n_output_packets(self):
        return self._n_output_packets

    @property
    def n_outputs(self):
        return self._n_outputs

    @property
    def output_channel_name(self):
        return "nengo_io_c2h_chip_%d" % self.idx

    def create(self, nxsdk_board, max_spikes_per_step):
        self.chip_id = nxsdk_board.n2Chips[self.idx].id
        chip_buffer_size = roundup(
            max(
                self.n_outputs,  # currently, buffer needs to hold all outputs
                Snips.channel_packet_elements
                + max(SpikePacker.size, Snips.error_info_size),
            ),
            Snips.channel_packet_elements,
        )

        # --- create IO snip
        c_path = os.path.join(self.tmp_snip_dir, "nengo_io_chip_%d.c" % self.idx)
        h_filename = "nengo_io_chip_%d.h" % self.idx
        logger.debug(
            "Creating %s with %d outputs, %d error, %d cores, %d probes",
            c_path,
            self.n_outputs,
            self.n_errors,
            len(self.cores),
            len(self.probes),
        )

        Snips.render_template(
            "nengo_io.c",
            c_path,
            header_file=h_filename,
            n_outputs=self.n_outputs,
            n_output_packets=self.n_output_packets,
            n_errors=self.n_errors,
            buffer_size=chip_buffer_size,
            packet_elements=Snips.channel_packet_elements,
            input_channel=self.input_channel_name,
            output_channel=self.output_channel_name,
            cores=self.cores,
            probes=self.probes,
        )

        # write header file using template
        Snips.render_template("nengo_io.h", os.path.join(self.tmp_snip_dir, h_filename))

        # create SNIP process
        logger.debug("Creating nengo_io chip %d process", self.idx)
        self.io_snip = nxsdk_board.createSnip(
            name="nengo_io_chip" + str(self.chip_id),
            cFilePath=c_path,
            includeDir=self.tmp_snip_dir,
            funcName="nengo_io",
            guardName="guard_io",
            phase=SnipPhase.EMBEDDED_MGMT,
            chipId=self.chip_id,
        )

        # --- create learning snip
        h_filename = "nengo_learn_chip_%d.h" % self.idx
        c_path = os.path.join(self.tmp_snip_dir, "nengo_learn_chip_%d.c" % self.idx)

        # write c file using template
        Snips.render_template("nengo_learn.c", c_path, header_file=h_filename)

        # write header file using template
        Snips.render_template(
            "nengo_learn.h", os.path.join(self.tmp_snip_dir, h_filename)
        )

        # create SNIP process
        logger.debug("Creating nengo_learn chip %d process", self.idx)
        self.learn_snip = nxsdk_board.createSnip(
            name="nengo_learn",
            cFilePath=c_path,
            includeDir=self.tmp_snip_dir,
            funcName="nengo_learn",
            guardName="guard_learn",
            phase=SnipPhase.EMBEDDED_PRELEARN_MGMT,
            chipId=self.chip_id,
        )

        # --- create channels
        input_channel_size = (
            self.output_header_len  # first int stores number of spikes
            + max_spikes_per_step * SpikePacker.size
            + self.total_error_len
        )
        logger.debug(
            "Creating %s channel (%d)", self.input_channel_name, input_channel_size
        )
        self.input_channel = nxsdk_board.createChannel(
            self.input_channel_name.encode(),
            numElements=input_channel_size,  # channel size (in elements)
            messageSize=Snips.packet_bytes,  # size of one packet (in bytes)
            slack=16,  # size of send/receive buffer on chip/host (in packets)
        )
        logger.debug(
            "Creating %s channel (%d)", self.output_channel_name, self.n_outputs
        )
        self.output_channel = nxsdk_board.createChannel(
            self.output_channel_name.encode(),
            numElements=self.n_outputs,  # channel size (in elements)
            messageSize=Snips.packet_bytes,  # size of one packet (in bytes)
            slack=16,  # size of send/receive buffer on chip/host (in packets)
        )

    def prepare_for_probe(self, block, pinfo, target_idx):
        chip_idx = pinfo.chip_idx[target_idx]
        core_id = pinfo.core_id[target_idx]
        compartment_idxs = pinfo.compartment_idxs[target_idx]

        self.cores.add(core_id)

        key = pinfo.key
        if key == "spike":
            refract_delay = block.compartment.refract_delay[0]
            assert np.all(block.compartment.refract_delay == refract_delay)
            key = refract_delay * 128

        n_comps = len(compartment_idxs)
        logger.info(n_comps)
        comp0 = compartment_idxs[0]
        comp_diff = np.diff(compartment_idxs)
        is_ranged_comps = np.all(
            comp_diff == comp_diff[0] if len(comp_diff) > 0 else False
        )
        is_packed_spikes = is_ranged_comps and (pinfo.key == "spike")
        n_packed_spikes = n_comps if is_packed_spikes else 0

        output_len = ceil_div(n_comps, 32) if is_packed_spikes else n_comps
        output_slice = slice(self.last_output, self.last_output + output_len)
        pinfo.snip_range.append((chip_idx, output_slice, n_packed_spikes))

        offset = self.output_offset + self.last_output
        if is_ranged_comps:
            self.probes.append((offset, key, core_id, comp0, comp_diff[0], n_comps))
        else:
            for i, comp in enumerate(compartment_idxs):
                self.probes.append((offset + i, key, core_id, comp, 0, 1))
        self.last_output += output_len


class HostSnip:
    recv_retries = 10
    recv_size = 4096  # python docs recommend small power of 2, e.g. 4096
    recv_timeout = 0.01

    def __init__(self, tmp_snip_dir):
        self.tmp_snip_dir = tmp_snip_dir

        self.connected = False
        self.snip = None

        self.port = np.random.randint(50000, 60000)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

    def connect(self, nxsdk_board):
        # pause to allow host snip to start and listen for connection
        time.sleep(0.1)

        host_address = nxsdk_board.executor._host_coordinator.hostAddr
        logger.info("Connecting to host socket at (%s, %s)", host_address, self.port)
        self.socket.connect((host_address, self.port))
        self.connected = True

    def close(self):
        # send -1 to signal host/chip that we're done
        self.send_all([-1])

        # pause to allow chip to receive -1 signal via host
        time.sleep(0.1)

        self.socket.close()
        self.connected = False

    def create(self, nxsdk_board, chip_snips):
        read_size = roundup(1024, Snips.channel_packet_elements)
        write_packets = ceil_div(read_size, Snips.channel_packet_elements)
        write_size = write_packets * Snips.channel_packet_elements
        # double buffer size, just so we can do a full extra read/write if we need to
        buffer_size = 2 * roundup(
            max(read_size, write_size), Snips.channel_packet_elements
        )

        cpp_path = os.path.join(self.tmp_snip_dir, "nengo_host.cpp")
        Snips.render_template(
            "nengo_host.cpp",
            cpp_path,
            n_chips=len(chip_snips),
            buffer_size=buffer_size,
            packet_size=Snips.channel_packet_elements,
            read_size=read_size,
            write_packets=write_packets,
            output_packets=", ".join(
                "%d" % chip_snip.n_output_packets for chip_snip in chip_snips
            ),
            server_port=self.port,
            input_channels=[chip_snip.input_channel_name for chip_snip in chip_snips],
            output_channels=[chip_snip.output_channel_name for chip_snip in chip_snips],
        )

        # make process
        self.snip = nxsdk_board.createSnip(
            phase=SnipPhase.HOST_CONCURRENT_EXECUTION, cppFile=cpp_path
        )

    def recv_bytes(self, bytes_expected):
        data = bytearray([])
        n_retries = 0

        while len(data) < bytes_expected and n_retries < self.recv_retries:
            ready, _, _ = select([self.socket], [], [], self.recv_timeout)
            if self.socket in ready:
                data += bytearray(self.socket.recv(self.recv_size))
            else:  # pragma: no cover
                n_retries += 1

        if len(data) < bytes_expected:
            raise RuntimeError(
                "Received (%d) less than expected (%d)" % (len(data), bytes_expected)
            )

        last_val = np.frombuffer(data[-4:], np.int32).item()
        logger.debug("Received %d bytes, last_val=%d", len(data), last_val)
        if last_val == -1:
            raise RuntimeError("Received shutdown signal from chip")

        return np.frombuffer(data, dtype=np.int32)

    def send_all(self, data):
        msg_bytes = struct.pack("%di" % len(data), *data)
        self.socket.sendall(msg_bytes)


class SpikePacker:
    """Packs spikes for sending to chip

    Currently represents a spike as two int32s.
    """

    size = 2  # must match nengo_io.c.template

    @classmethod
    def pack(cls, spikes):
        """Pack the spike into a tuple of 32-bit integers.

        Parameters
        ----------
        spike : structured ndarray of spikes
            The spikes to pack.

        Returns
        -------
        packed_spike : tuple of int
            A tuple of length ``size * n_spikes`` to represent this spike.
        """
        if len(spikes) == 0:
            return []

        assert np.all(
            spikes["chip_id"] == spikes["chip_id"][0]
        ), "All spikes must go to the same chip"
        assert np.all(spikes["core_id"] < 1024)
        assert np.all(spikes["axon_id"] < 4096)
        assert np.all(spikes["axon_type"] <= 32)
        assert np.all(spikes["atom"] < 1024)

        axon_type = spikes["axon_type"]
        axon_type[axon_type == 16] += spikes["atom_bits_extra"][axon_type == 16]
        return np.array(
            [
                np.left_shift(spikes["core_id"], 16) + spikes["axon_id"],
                np.left_shift(axon_type, 16) + spikes["atom"],
            ]
        ).T.ravel()
