from controller_example import Controller

from weap_util.weap_container import run

def main():
    controller = Controller()
    run(controller, "config_example_map.yaml")

if __name__ == "__main__":
    main()