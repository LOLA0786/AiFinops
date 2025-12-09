from aifinops.omnimode_ultra.ultra_core import OmniModeUltra

if __name__ == "__main__":
    ultra = OmniModeUltra()
    for _ in range(5):
        out = ultra.run_cycle()
        print("\\n=== OMNIMODE ULTRA CYCLE ===")
        print(out)
