import sys
import unittest
import port_scanner


if __name__ == "__main__":
    if "--test" in sys.argv:
        tests = unittest.defaultTestLoader.discover("tests")
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        if not result.wasSuccessful():
            sys.exit(1)
    elif "--official-tests" in sys.argv:
        tests = unittest.defaultTestLoader.loadTestsFromName("test_module")
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        if not result.wasSuccessful():
            sys.exit(1)
    else:
        target = "127.0.0.1"
        start = 8000
        end = 8000
        verbose = False

        if len(sys.argv) > 1:
            target = sys.argv[1]
        if len(sys.argv) > 3:
            try:
                start = int(sys.argv[2])
                end = int(sys.argv[3])
            except ValueError:
                print("Ports must be whole numbers")
                sys.exit(1)
        if "--verbose" in sys.argv:
            verbose = True

        try:
            print(port_scanner.get_open_ports(target, [start, end], verbose))
        except ValueError as error:
            print(error)
            sys.exit(1)
