from os import listdir,system
from time import time,sleep
from aj_progressB import Bar

class Procesar_Similares():

    def __init__(self,files):
        self.files=files


    def buscar(self,percent_match,reprocesar=False):
        if self.files:
            cont = 0
            files=list(map(lambda x:[x,True],self.files))

            if not reprocesar:
                self.files=[]
            texto='\nReprocesando al {0}%: ' if reprocesar else '\nBuscando al {0}%: '
            bar = Bar(texto.format(percent_match), max_val1=len(files))

            while cont < len(files):

                if files[cont][1]:  # si el archivo seleccionado no ha dado similar .

                    archivo = files[cont][0]

                    l_archivos_comp = files[cont + 1:]  # lista de archivos a comparar con el archivo seleccionado

                    if l_archivos_comp:  # si existen archivos para comparar con el archivo seleccionado

                        bar.set_max_val(len(l_archivos_comp))

                        similar_general = (101, '')

                        for archivo_comp in l_archivos_comp:

                            if archivo_comp[1]:  # si el archivo a comparar seleccionado no a dado similar

                                match = self._comparar(archivo, archivo_comp[0])
                                #print('{2}{3} {0} == {1}'.format(archivo,archivo_comp[0],reprocesar,match[0]))
                                if match[0] > percent_match:
                                    # print(match)
                                    archivo_comp[1] = False
                                    if similar_general[0] > match[0]:
                                        similar_general = match

                                    if reprocesar:self.files.remove(archivo_comp[0])



                            bar.update()

                        if similar_general[0] != 101:
                            self.files.append(similar_general[1])
                            if reprocesar:self.files.remove(archivo)

                cont += 1
                bar.update1()
            #print('\n\n[{0}]\n\n'.format(','.join(self.files)))
            print('\nSimilares: {0}'.format(len(self.files)))

    def _comparar(self,nombre='', nombre2=''):
        'Compara dos textos y devuelve el porciento de similitud y el fragmento comun'
        caract_selec_min = 2

        similar = (0, '')
        len_nombre = len(nombre)
        len_nombre2 = len(nombre2)

        for cant_caract in range(caract_selec_min, len_nombre + 1):

            for cont_ini in range(len_nombre - cant_caract + 1):

                seleccion = nombre[cont_ini:cant_caract + cont_ini]
                if seleccion in nombre2:
                    if cant_caract > similar[0]:
                        similar = (cant_caract, seleccion)

        total = len_nombre if len_nombre > len_nombre2 else len_nombre2
        return (similar[0] * 100) / total, similar[1]

def inicio():

    ini = time()
    print('\nOrganizando archivos:\n')
    archivos = listdir()
    archivos1 = []
    arch_v=[]

    def mover_existentes(nombre,archivos):
        if nombre in archivos:
            #Ya hay archivos similares de búsquedas pasadas
            arch_v=listdir(nombre)

            if not 'Errores' in archivos:
                system('mkdir Errores')

            for arch_o in arch_v:

                system(f'mv *"{arch_o}"* {nombre}/"{arch_o}" 2>>Errores/errores_{nombre}.txt')
                sleep(0.1)
            sleep(3)
            #archivos = listdir()
            return arch_v,listdir()
        return [],archivos
    #'Organizados'

    arch_v,archivos=mover_existentes('Organizados',archivos)

    archivos = mover_existentes('Borrar', archivos)[1]



    for arch in archivos:
        # quitar extension y carpetas
        # lista_negra={'Episodio':'','[1080p]':''}

        arch_mod = '.'.join(arch.split('.')[:-1])

        '''for pal in lista_negra:
            arch_mod=arch_mod.replace(pal,lista_negra[pal])'''

        if arch_mod: archivos1.append(arch_mod)

    proc=Procesar_Similares(archivos1)

    proc.buscar(85)
    proc.buscar(90,True)

    if proc.files:

        #print('\n\nCaracteres similares: {0}'.format(len(proc.files)))
        #print('Reprocesando resultados: {0}'.format(len(proc.similares_proc)))

        #moviendo archivos
        if not 'Organizados' in archivos:
            system('mkdir Organizados')
        if not 'Errores' in archivos:
            system('mkdir Errores')
        if not 'Borrar' in archivos:
            system('mkdir Borrar')

        for similar in proc.files:

            while similar[-1]==' ' or similar[-1]=='.':
                #quitar el espacio y el punto despues de la palabra
                similar=similar[:-1]

            if not similar in arch_v:
                system('mkdir Organizados/"{0}"'.format(similar))



            system('mv *"{0}"* Organizados/"{0}" 2>Errores/errores_similares.txt'.format(similar))


    print('\nTerminado en {0} segundos.'.format(round((time()-ini),2)))

if __name__ == '__main__':inicio()