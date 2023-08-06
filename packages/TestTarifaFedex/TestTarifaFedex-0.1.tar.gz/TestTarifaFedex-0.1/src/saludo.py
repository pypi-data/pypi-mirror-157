class Saludo:
    def __init__(self,nombre = str):
        self.__nombre = nombre

    def saludo_jasso(self):
        return "hola " + self.__nombre

