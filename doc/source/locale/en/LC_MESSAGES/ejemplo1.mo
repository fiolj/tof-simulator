��          �               ,  \   -  	   �  "   �  ^   �  s     H   �  �   �  	   T     ^  I   q  {   �  b   7  c   �     �  C     6   R  �  �  @        V     c  D   |  Y   �  ?     x   [     �     �  K   �  ~   ;	  F   �	  b   
     d
  \   g
  2   �
   Agregamos algunas sustancias a las cuales le vamos a simular las señales de tiempo de vuelo Cálculos Ejemplos de uso del módulo tofsim El método ``ToF.signal()`` devuelve la simulación de la señal que se observaría en el TOF. El objeto del tipo ``ToF`` contiene toda la información sobre los parámetros de construcción y de funcionamiento El resultado es un diccionario donde cada elemento es un array de datos: Este método ofrece algo de flexibilidad, pero dado que los datos se guardan como numpy arrays, se pueden graficar separadamente Gráficos Iniciar la sesión La manera más simple de graficar es utilizando el método ``make_plot``. Notar que en realidad no es necesario guardar el valor de ``s`` en este caso ya que queda guardado en el objeto ``T.times`` Para iniciar la sesión, importamos el paquete o sólo el objeto ``ToF`` Por ejemplo, en la forma: los restantes elementos ``s[sustancia]`` tienen los valores de señal producida por cada sustancia. o, simplemente: s[‘signal’] tiene los valores de la suma de todas las especies. s[‘time’] tiene el eje x, con la ventana de tiempo Project-Id-Version: TOF-simulator version: 2.9
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2020-08-02 10:20-0300
PO-Revision-Date: 2020-08-02 12:55-0300
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: en
Language-Team: en <LL@li.org>
Plural-Forms: nplurals=2; plural=(n != 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.8.0
 We add some substances, for simulation of time-of-fligth signals Calculations Example of use of tofsim The method ``ToF.signal()`` returns the simulated signal of the TOF. The object ``ToF`` keeps the information on all the construction and operation parameters The result is a dictionary, where each element is a data array: This method allows for some customization. Also, since the data is kept in numpy arrays it may be plotted independently: Plotting Start the session The simplest way of plotting the signals is using the method ``make_plot``. Note that it is not necessary to keep the value of ``s`` in the above example, it is kept in the ``ToF`` object as ``T.times`` Import the package, or simply the object ``ToF`` For instance, either: All other elements, of the form ``s[substance]`` have the values of the signal for each substance. or s[‘signal’] has the resultant signal, summing the individual signal for all the species. s[‘time’] the x-axis, contains the time-window 