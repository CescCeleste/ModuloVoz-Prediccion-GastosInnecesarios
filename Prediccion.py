from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFillRoundFlatButton
import sqlite3
import os
import datetime
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from plyer import tts
import speech_recognition as sr
from kivy.uix.popup import Popup
from io import open
import numpy as np
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog




class pantalla(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
   
    
    def voz_boton(self, texto):
        hoy = datetime.date.today()
        print(hoy)
        self.ids.txt_Fecha.text = str(hoy)
        r= sr.Recognizer()
        #leyenda= self.ids.btn_Producto.text
        print(texto)
        try:
            tts.speak("Ingrese "+texto)
            #print ("Escuchando")
            with sr.Microphone() as source:
                #r.adjust_for_ambient_noise(source)
                #print("Hable ahora...")
                audio = r.listen(source)
                entrada = r.recognize_google(audio, language='es-ES')
                if (texto=='Nombre'):
                    self.ids.txt_Producto.text = entrada
                elif(texto=='Precio'):
                    self.ids.txt_Precio.text = entrada
                elif(texto=='Cantidad'):
                    self.ids.txt_Cantidad.text = entrada
                   
            
        except NotImplementedError:
            popup = ErrorPopup()
            popup.open()
        except:
            print("No entendí o tardó demasiado")
            
    
    def accion(self):
        APP_PATH = os.getcwd()
        DB_PATH = APP_PATH+'/prueba.db' #SE DEBE CAMBIAR EL NOMBRE AL NOMBRE DE LA BD FINAL
        con = sqlite3.connect(DB_PATH) #CONEXION A LA BD
        cursor = con.cursor() #CURSOR PARA EJECUTAR QUERYS
        
        producto= self.ids.txt_Producto.text
        precio= self.ids.txt_Precio.text
        cantidad= self.ids.txt_Cantidad.text
        fecha= self.ids.txt_Fecha.text
        
        cursor.execute("""SELECT ID FROM PRODUCTOS""")
        id_mayor= max(cursor)
        num_id= id_mayor[0]
        id_nuevo= num_id+1
        print("El proximo id es: ",id_nuevo)
        
        datos=[id_nuevo, producto, precio, cantidad, fecha]
        try:
            cursor.execute("""INSERT INTO PRODUCTOS VALUES(?, ?, ?, ?, ?)""", datos)
            con.commit()
        except Exception as e:
            print(e)
        
        for i in datos:
            print(i)
        
        con.close()
        ####CREAR TXT FECHA
        self.creatxtFechas(producto, fecha, cantidad)
        ####CREAR TXT TABLA
        self.creatxtTabla(producto)
        ####CREAR TXT PREDICCION
        self.prediccion(producto, cantidad, fecha)
        
        
     
    def creatxtFechas(self, producto, fecha, cantidad):
        print("Crea el txt e inserta las fechas y cantidad de productos")
        archivo_fechas= open(producto+"_Fechas.txt", "a")
        archivo_fechas.write(cantidad+" "+fecha+"\n")
        archivo_fechas.close()
        archivo_tablas=open(producto+"_Tabla.txt", "a")
        #lin= archivo_tablas.read()
        archivo_tablas.close()
        return
    
    def creatxtTabla(self, producto):
        archivo= open(producto+"_Fechas.txt", "r")  #abrir el archivo-- el nombre no es estático

        lineas= archivo.readlines() #se obtienen las lineas del archivo
        print(lineas)
        archivo.close() #se cierra el archivo
        
        print(len(lineas))
        if (len(lineas)>=2): #se verifica que haya más de una linea de información 
            ultima= lineas[len(lineas)-1]
            print(len(ultima))
            penultima =lineas[len(lineas)-2]
            print(len(penultima))
            
            if(len(ultima)==14):        #se ontienen las fechas dependiendo del largo de las cadenas
                ultimaF=ultima[3:13]
                
            elif(len(ultima)==13):
                ultimaF=ultima[2:12]
                
            if(len(penultima)==14):
                penultimaF=penultima[3:13]
                cantidad=penultima[0:2]
                
            elif(len(penultima)==13):
                penultimaF=penultima[2:12]
                cantidad=penultima[0]
        
            ultima_fecha= datetime.datetime.strptime(ultimaF, '%Y-%m-%d').date() #se pasa la fecha a tipo date
            print(ultima_fecha)
            
            penultima_fecha=datetime.datetime.strptime(penultimaF, '%Y-%m-%d').date() #se pasa la fecha a tipo date
            print(penultima_fecha)
                
            print("la cantidad de elementos es "+cantidad)
            
            dias= str((ultima_fecha - penultima_fecha).days) #se obtiene el numero de días entre las fechas
            print(dias)
            
            datos= cantidad+" "+dias #se crea la cadena que ingresa al nuevo txt
            print(datos)
            nuevo_archivo=open(producto+"_Tabla.txt", "a")
            nuevo_archivo.write(datos+"\n")
            nuevo_archivo.close()
            
        elif(len(lineas)==1):
            print("datos insuficientes para generar regresión lineal")
        
        return


    def prediccion(self, producto, cantidad, fecha):
        print("seccion prediccion")
        fechaN= datetime.datetime.strptime(fecha, '%Y-%m-%d').date() 
        archivo_datos= open(producto+"_Tabla.txt", "r") #abrir el archivo
        renglones= archivo_datos.readlines() #se obtienen los renglones del txt
        archivo_datos.close()
        
        print(renglones)
        x_numero_elementos=[]
        y_dias=[]
        
        
        for i in renglones:
            largo_cadena= len(i)
            if(largo_cadena==4):
                numero=int(i[0])
                dias=int(i[2])
                x_numero_elementos.append(numero)
                y_dias.append(dias)
                
            elif(largo_cadena==5):
                if(i[1]==" "):
                    numero=int(i[0])
                    dias=int(i[2:4])
                    x_numero_elementos.append(numero)
                    y_dias.append(dias)
                elif(i[2]==" "):
                    numero=int(i[0:2])
                    dias=int(i[3])
                    x_numero_elementos.append(numero)
                    y_dias.append(dias)
            elif(largo_cadena==6):
                numero=int(i[0:2])
                dias=int(i[3:5])
                x_numero_elementos.append(numero)
                y_dias.append(dias)
        
        print(x_numero_elementos)
        print(y_dias)
        
        x= np.array(x_numero_elementos)
        print(x)
        y= np.array(y_dias)
        print(y)
        n=len(renglones)
        print(n)
        
        if(n==0 or n==1):
            print("No hay suficientes datos para generar la predicción")
            cadenaDialog="No hay suficientes datos para generar la predicción"
        else: 
            sumx= sum(x)
            print(sumx)
            sumy= sum(y)
            print(sumy)
            sumx2= sum(x*x)
            print(sumx2)
            sumxy= sum(x*y)
            print(sumxy)
            promx= sumx/n
            print(promx)
            promy= sumy/n
            print(promy)
            
            m=((n*sumxy)-(sumx*sumy))/((n*sumx2)-(sumx*sumx))
            b= promy-(m*promx)
            
            print(m, b)
            cant= int(cantidad)
            
            fx= int(m*cant+b)
            print("Tu producto pueden terminarse en ", fx," dias")
            pred= fechaN + datetime.timedelta(days=fx)
            print("La fecha prevista para que se termine tu producto es: ",pred)
            fechaPred=str(pred)
            cadenaDialog="La fecha prevista para que se termine tu producto es: "+fechaPred
            
            self.dialog= MDDialog(title = "Prediccion de faltantes", #CUADROD DE DIALOGO PARA OBTENER EL PERIODO DEL REPORTE DE GASTOS
                               text = cadenaDialog,
                               size_hint=[.9, .9],
                               auto_dismiss=True,
                               buttons=[
                                   MDFlatButton(
                                   text="Cerrar",
                                   on_release=self.dialog_close)
                               ]
                               )
            self.dialog.open()
        
            ###crear el txt con las fechas predichas
            archivo_fechasPred= open(producto+"_FechasPred.txt", "a")
            archivo_fechasPred.write(fechaPred+"\n")
            archivo_fechasPred.close()
        return
    
    def dialog_close(self, *args): # Cierra el dialog del boton ayuda
        #print("Cerrando Dialog")
        self.dialog.dismiss()
            
    
class modPredApp(MDApp):
    def build(self):
        self.title = "Modulo de acceso por voz"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.bg_light
        return pantalla()
    
class ErrorPopup(Popup):
    pass
      
    
        
        
modPredApp().run()