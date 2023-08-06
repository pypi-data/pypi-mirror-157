# std
import argparse

parser = argparse.ArgumentParser(description='laz cli')

parser.add_argument('--verbose', '-v', action='count', default=0, help='Set logging verbosity')
