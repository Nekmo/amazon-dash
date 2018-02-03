class InstallException(Exception):
    name = 'Install Error'
    tpl = '[{name}] {body}'

    def __init__(self, body='No details'):
        self.body = body

    def __str__(self):
        return self.tpl.format(name=self.name, body=self.body)


class IsInstallableException(InstallException):
    name = 'Unable to install'


class IsNecessaryException(InstallException):
    name = 'Already installed'