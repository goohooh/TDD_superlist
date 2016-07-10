from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

env.forward_agent = True
env.use_ssh_config = True

REPO_URL = 'https://github.com/goohooh/TDD_superlist.git'

def deploy():
    run('sudo apt-get update')
    run('sudo apt-get upgrade')
    run('sudo apt-get install git nginx')
    project_folder = '/home/ubuntu/TDD_superlist'
    # _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(project_folder)
    _update_settings(project_folder)
    _update_virtualenv(project_folder)
    _update_static_files(project_folder)
    _update_database(project_folder)

def _get_latest_source(project_folder):
    if exists(project_folder + '/.git'):
        run('cd %s && git fetch' % (project_folder,))
    else:
        run('git clone %s' % (REPO_URL))

    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (project_folder, current_commit))

def _update_settings(project_folder):
    settings_path = project_folder + '/superlist/superlist/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS = .+$',
        'ALLOWED_HOSTS = ["op.noreeter.com"]'
    )
#    secret_key_file = project_folder + '/superlist_key.py'
#    if not exists(secret_key_file):
#        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*('
#        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
#        append(secret_key_file, "SECRET_KEY = '%s'" %(key,))
#    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(project_folder):
#    pyenv = '~/.pyenv'
#    if exists(pyenv):
#        run('pyenv activate TDD_superlist')
#        run('pip install -r requirements.txt')
#        return
    bash_profile = '~/.bash_profile'
    if not exists(bash_profile):
        run('touch ~/.bash_profile')
    run('sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils')
    run('curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash')
    append(bash_profile, 'export PATH="~/.pyenv/bin:$PATH"')
    append(bash_profile, 'eval "$(pyenv init -)"')
    append(bash_profile, 'eval "$(pyenv virtualenv-init -)"')
    run('source .bash_profile')
    # run('pip install autoenv')
    # run('"source ~/.autoenv/activate.sh" >> ~/.bash_profile')
    # run('pyenv install 3.5.1')
    # run('pyenv virtualenv 3.5.1 TDD_superlist')
    run('source ~/.pyenv/versions/TDD_superlist/bin/activate TDD_superlist')
    run('cd TDD_superlist && ~/.pyenv/versions/TDD_superlist/bin/pip install -r requirements.txt')

def _update_static_files(project_folder):
    run('cd %s && ~/.pyenv/versions/TDD_superlist/bin/python superlist/manage.py collectstatic --noinput' % (project_folder,))

def _update_database(project_folder):
    run('mkdir -p %s' % (project_folder + '/database'))
    run('cd %s && ~/.pyenv/versions/TDD_superlist/bin/python superlist/manage.py makemigrations lists' % (project_folder,))
    run('cd %s && ~/.pyenv/versions/TDD_superlist/bin/python superlist/manage.py migrate' % (project_folder,))
