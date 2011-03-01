
from os.path import dirname, join, abspath

root_path = abspath(dirname(__file__))
repository_path = abspath(join(root_path, '..'))
templates_path = join(root_path, 'templates')
static_path = join(root_path, 'static')
index_name = 'Index'

data_path = join(root_path, 'data')
