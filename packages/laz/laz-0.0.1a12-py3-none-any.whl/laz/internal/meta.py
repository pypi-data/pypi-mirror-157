name = 'laz'
try:
    import pkg_resources
    version = pkg_resources.get_distribution(name).version
except:
    version = '0.0.0'
