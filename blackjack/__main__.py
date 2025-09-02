try:  # pragma: no cover - fallback for direct execution
    from .gui import SimulatorGUI
except ImportError:  # pragma: no cover
    from gui import SimulatorGUI  # type: ignore


def run_gui():
    gui = SimulatorGUI()
    gui.run()


if __name__ == "__main__":
    run_gui()
