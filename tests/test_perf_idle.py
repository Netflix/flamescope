import pytest

from app import config
from app.perf.flame_graph import perf_generate_flame_graph
from app.perf.heatmap import perf_read_offsets


@pytest.mark.parametrize('dispatcher', ['__do_softirq', '__softirqentry_text_start', 'handle_softirqs'])
def test_interrupted_idle_stack(tmp_path, monkeypatch, dispatcher):
    monkeypatch.setattr(config, 'PROFILE_DIR', str(tmp_path))
    path = tmp_path / 'sample.perf'
    idle = '\tffff arch_cpu_idle+0x4 ([kernel.kallsyms])\n'
    work = ('\tfffc tasklet_action+0x8 ([kernel.kallsyms])\n'
            '\tfffd %s+0x2 ([kernel.kallsyms])\n' % dispatcher)
    path.write_text('swapper 0 [000] 1.100: cycles:\n' + idle + '\n' +
                    'swapper 0 [000] 1.200: cycles:\n' + work + idle + '\n' +
                    'swapper 0 [000] 1.300: cycles:\n' + idle + '\n')

    assert perf_read_offsets(str(path)).offsets == [1.2]
    tree = perf_generate_flame_graph(str(path))
    swapper, = tree['c']
    idle_frame, = swapper['c']
    assert idle_frame['v'] == 0
    handler, = idle_frame['c']
    assert handler['n'] == dispatcher
    tasklet, = handler['c']
    assert (tasklet['n'], tasklet['v']) == ('tasklet_action', 1)
