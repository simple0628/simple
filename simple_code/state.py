"""全局共享状态"""

import threading

# AI 执行期间的中断标志，按 ESC 时 set
interrupt = threading.Event()
