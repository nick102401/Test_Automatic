import configparser
import os

proDir = os.path.split(os.path.realpath(__file__))[0]
configPath = os.path.join(proDir, "config.ini")


class ReadConfig:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(configPath)

    def get_global(self, param):
        value = self.config.get('global_paras', param)
        return value

    def get_mail(self, param):
        value = self.config.get('mail', param)
        return value

    def get_database(self, param):
        value = self.config.get('database', param)
        return value

    def get_conf(self, section, param):
        value = self.config.get(section, param)
        return value

    def set_conf(self, section, value, text):
        """
        配置文件修改
        :param section:
        :param value:
        :param text:
        :return:
        """
        self.config.set(section, value, text)
        with open(configPath, "w+") as f:
            return self.config.write(f)

    def add_conf(self, section_name):
        """
        添加类别到配置环境里
        :param section_name:
        :return:
        """
        self.config.add_section(section_name)
        with open(configPath, "w+") as f:
            return self.config.write(f)


if __name__ == '__main__':
    rc = ReadConfig()
    print(rc.get_mail('mail_host'))
