# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 10:07:50 2020

@author: evule
"""

import pandas as pd
import numpy as np

df=pd.read_excel('Triangulo.xlsx')
df['Year']=pd.DatetimeIndex(df['Fecha Pago']).year

Origen=pd.DataFrame({'ID':[1,2,3], 'Origin Year': [2010,2009,2015]})

df=pd.merge(df, Origen, on='ID')

df['Edad']=df['Year']-df['Origin Year']+1
df=df.groupby(['Origin Year','Edad'], as_index=False)['Monto'].sum()

Hoy=2015
n1=len(df.groupby('Origin Year')['Origin Year'].count())
n2=Hoy-df['Origin Year'].min()+1

#Agrego filas vacias si no hubieron datos. Primero hago list*n para que me mantenga el orden. Y para Origin Year tengo q hacer repeat
df2=pd.DataFrame({'Edad': list(range(1,Hoy-df['Origin Year'].min()+2))*n1, 'Monto':0,'Origin Year':pd.Series(list(set(df['Origin Year']))).repeat(n2)})

df.set_index(['Origin Year','Edad'], inplace=True)
df2.set_index(['Origin Year','Edad'], inplace=True)

df2.Monto=df.Monto #Iguala por indice
df2=df2.fillna(0)

df2=df2.unstack(level='Edad')
df2=np.cumsum(df2, axis=1)
df2.columns=df2.columns.droplevel()


df2['Aux']=Hoy-df2.index+1

FDI=pd.DataFrame(0,index=range(1),columns=df2.columns)


for i in range(1,len(df2.columns)-1):
    Numerador=df2[df2.loc[:,'Aux']>=i+1].iloc[:,i].sum()
    Denominador=df2[df2.loc[:,'Aux']>=i+1].iloc[:,i-1].sum()
    FDI.iloc[:,i]=Numerador/Denominador #la columna 2 es para crecer de 1 a 2

FDI=FDI.drop(['Aux'],1)
FDI=FDI.iloc[:,1:]

FDA=pd.DataFrame(np.cumprod(FDI, axis=1).transpose()) #Factor de Desarrollo Acumulado
FDA.reset_index(inplace=True)
FDA.rename(columns={FDA.columns[-1]:'FDA'}, inplace=True)
print(FDA)

Ultimate=pd.DataFrame(df2.iloc[:,-2:])
Ultimate.columns=df2.columns[-2:]
Ultimate['Aux']+=1 #le sumo 1 para que tenga la misma logica que FDA
Ultimate.rename(columns={'Aux':'Edad'}, inplace=True)
Ultimate=pd.merge(Ultimate,FDA, on='Edad', how='left')
Ultimate['FDA']=Ultimate['FDA'].fillna(1)

Ultimate['Edad']-=1 #vuelvo
Ultimate['SiniestrosUltimate']=Ultimate.iloc[:,0]*Ultimate['FDA']
print(Ultimate)


