import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from inline_sql import sql, sql_val

data = pd.read_csv("NY-House-Dataset.csv")
print(data)

consultaPrecios = """
                SELECT PRICE
                FROM data
                """

precios = sql^consultaPrecios

#OUTLIERS

# primer cuartil
q1 = np.quantile(precios, 0.25)
 
# tercer cuartil
q3 = np.quantile(precios, 0.75)
med = np.median(precios)
 
# reg intercuartil
iqr = q3-q1
 
# maximo y minimo
upper_bound = q3+(1.5*iqr)
lower_bound = q1-(1.5*iqr)

precios2 = np.array(precios)
precios2 = precios2[(precios > lower_bound) & (precios < upper_bound)]

plt.figure(figsize=(8, 5))
plt.boxplot(precios2)
plt.show()

consultaPrecioPorCama = """
                        SELECT PRICE, BEDS
                        FROM data
                        WHERE PRICE > $lower_bound AND PRICE < $upper_bound
                        """

consultaPrecioPorTipo = """
                        SELECT PRICE, TYPE
                        FROM data
                        WHERE PRICE > $lower_bound AND PRICE < $upper_bound
                        """

precioPorCama = sql^consultaPrecioPorCama
precioPorTipo = sql^consultaPrecioPorTipo

consultaCamas = """
                SELECT DISTINCT BEDS, AVG(PRICE)
                FROM precioPorCama
                GROUP BY BEDS
                ORDER BY AVG(PRICE) ASC
                """

camas = sql^consultaCamas
plt.scatter(camas["BEDS"],camas["avg(PRICE)"])

#REGRESION ENTRE PROMEDIO DE  PRECIO Y CANTIDAD DE CAMAS

from sklearn.linear_model import LinearRegression

camasModelo = np.array(camas["BEDS"]).reshape(-1,1)
promedioModelo = np.array(camas["avg(PRICE)"])

model = LinearRegression().fit(camasModelo, promedioModelo)

r_sq = model.score(camasModelo, promedioModelo)
print(f"coefficient of determination: {r_sq}")

promedioPred = model.intercept_ + model.coef_*camasModelo

plt.figure(figsize=(8,5))
plt.plot(camasModelo,promedioPred, color="red")
plt.scatter(camasModelo,promedioModelo)
plt.show()

consultaTipo = """
                SELECT DISTINCT TYPE, AVG(PRICE)
                FROM precioPorTipo
                GROUP BY TYPE
                ORDER BY AVG(PRICE) DESC
                """

tipos = sql^consultaTipo
plt.pie(tipos["avg(PRICE)"],labels = tipos["TYPE"])
