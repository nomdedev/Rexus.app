#!/usr/bin/env python3

import sys
import traceback
sys.stdout.reconfigure(encoding='utf-8')

try:
    from rexus.modules.logistica.view import LogisticaView
    print("✅ Logística importa correctamente")
except Exception as e:
    print(f"❌ Error importando Logística: {e}")
    traceback.print_exc()