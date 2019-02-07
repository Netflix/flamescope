import re
#
# Parsing
#
# This file is part of FlameScope, a performance analysis tool created by the
# Netflix cloud performance team. See:
#
#    https://github.com/Netflix/flamescope
#
# Copyright 2018 Netflix, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# perf script output examples:
#
# Stack examples (-g):
#
# swapper     0 [021] 28648.467059: cpu-clock:
# 	ffffffff810013aa xen_hypercall_sched_op ([kernel.kallsyms])
# 	ffffffff8101cb2f default_idle ([kernel.kallsyms])
# 	ffffffff8101d406 arch_cpu_idle ([kernel.kallsyms])
# 	ffffffff810bf475 cpu_startup_entry ([kernel.kallsyms])
# 	ffffffff81010228 cpu_bringup_and_idle ([kernel.kallsyms])
#
# java 14375 [022] 28648.467079: cpu-clock:
# 	    7f92bdd98965 Ljava/io/OutputStream;::write (/tmp/perf-11936.map)
# 	    7f8808cae7a8 [unknown] ([unknown])
#
# swapper     0 [005]  5076.836336: cpu-clock:
# 	ffffffff81051586 native_safe_halt ([kernel.kallsyms])
# 	ffffffff8101db4f default_idle ([kernel.kallsyms])
# 	ffffffff8101e466 arch_cpu_idle ([kernel.kallsyms])
# 	ffffffff810c2b31 cpu_startup_entry ([kernel.kallsyms])
# 	ffffffff810427cd start_secondary ([kernel.kallsyms])
#
# swapper     0 [002] 6034779.719110:   10101010 cpu-clock:
#       2013aa xen_hypercall_sched_op+0xfe20000a (/lib/modules/4.9-virtual/build/vmlinux)
#       a72f0e default_idle+0xfe20001e (/lib/modules/4.9-virtual/build/vmlinux)
#       2392bf arch_cpu_idle+0xfe20000f (/lib/modules/4.9-virtual/build/vmlinux)
#       a73333 default_idle_call+0xfe200023 (/lib/modules/4.9-virtual/build/vmlinux)
#       2c91a4 cpu_startup_entry+0xfe2001c4 (/lib/modules/4.9-virtual/build/vmlinux)
#       22b64a cpu_bringup_and_idle+0xfe20002a (/lib/modules/4.9-virtual/build/vmlinux)
#
# bash 25370/25370 6035935.188539: cpu-clock:
#                   b9218 [unknown] (/bin/bash)
#                 2037fe8 [unknown] ([unknown])
# other combinations are possible.
#
# Some extra event-line examples (excluding stacks):
#
# java 52025 [026] 99161.926202: cycles:
# java 14341 [016] 252732.474759: cycles:      7f36571947c0 nmethod::is_nmethod() const (/...
# java 14514 [022] 28191.353083: cpu-clock:      7f92b4fdb7d4 Ljava_util_List$size$0;::call (/tmp/perf-11936.map)
#      swapper     0 [002] 6035557.056977:   10101010 cpu-clock:  ffffffff810013aa xen_hypercall_sched_op+0xa (/lib/modules/4.9-virtual/build/vmlinux)
#         bash 25370 6036.991603:   10101010 cpu-clock:            4b931e [unknown] (/bin/bash)
#         bash 25370/25370 6036036.799684: cpu-clock:            4b913b [unknown] (/bin/bash)
# other combinations are possible.
#
# Some extra stack-line examples:
#
#           7fa4c651fb95 CardTableModRefBS::process_stride(Space*, MemRegion, int, int, OopsInGenClosure*, CardTableRS*, signed char**, unsigned long, unsigned long) (/usr/lib/jvm/java-8-oracle-1.8.0.121/jre/lib/amd64/server/libjvm.so)
#
# This event_regexp matches the event line, and puts time in the first group:
#
event_regexp = re.compile(r" +([0-9.]+): .+?:")
frame_regexp = re.compile(r"^[\t ]*[0-9a-fA-F]+ (.+) \((.*?)\)$")
comm_regexp = re.compile(r"^ *([^0-9]+)")

# idle stack identification. just a regexp for now:
idle_process = re.compile("swapper")
idle_stack = re.compile("(cpuidle|cpu_idle|cpu_bringup_and_idle|native_safe_halt|xen_hypercall_sched_op|xen_hypercall_vcpu_op)")
idle_regexp = re.compile("%s.*%s" % (idle_process.pattern, idle_stack.pattern))
