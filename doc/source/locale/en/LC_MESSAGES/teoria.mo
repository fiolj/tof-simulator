��          |               �      �   (   �        .   5  {   d  �   �  }   �  D     N   \  )   �  !   �  �  �     �  (   �     �  -   �       �   �  ^   =  ?   �  L   �  *   )     T   Condiciones iniciales Definiendo las cantidades adimensionales Ecuaciones de movimiento Implementación de cálculo de tiempo de vuelo La distribución de posición puede elegirse uniforme de ancho :math:`\delta s`, o *normal* con :math:`\sigma= \delta s/2`. La distribución de tiempos iniciales puede elegirse uniforme de ancho :math:`\delta t`, o *normal* con :math:`\sigma= \delta t/2`. El valor default es :math:`\delta t= 8~\mathrm{ns}`. La distribución de velocidades inicial en la dirección de aceleración está dada por la distribución de Maxwell-Boltzmann Las ecuaciones de movimiento para cada tramo del tiempo de vuelo son Los tiempos de vuelo para cada tramo serán (:math:`t_{j} = \sqrt{m}\,T_{j}`): con ancho :math:`\sigma = \sqrt{k_{B} T}` y resolviendo el tiempo obtenemos Project-Id-Version: TOF-simulator version: 2.9
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2020-08-02 14:12-0300
PO-Revision-Date: 2020-08-03 15:56-0300
Last-Translator: Juan Fiol <juanfiol@gmail.com>
Language: en
Language-Team: TOF <LL@li.org>
Plural-Forms: nplurals=2; plural=(n != 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.8.0
 Initial conditions By defining the dimensionless magnitudes Equations of motion Implementation of time-of-flight calculations The spatial distribution may be chosen either uniform with width :math:`\delta s`, or *normal* with :math:`\sigma= \delta s/2`. The time distribution also may be chosen either uniform of width :math:`\delta t`, or *normal* with :math:`\sigma= \delta t/2`. The default value is :math:`\delta t= 8~\mathrm{ns}`. Initial velocities are given by the Maxwell-Boltzmann distribution in the direction of the TOF The equations of motion for each stage of the spectrometer are: Time of flight for each stage is given by (:math:`t_{j} = \sqrt{m}\,T_{j}`): with width :math:`\sigma = \sqrt{k_{B} T}` and solving for time, we get 