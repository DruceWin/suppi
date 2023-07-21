import json

import pandas as pd
from pandas import DataFrame

with open("data.json", encoding="UTF8") as f:
    raw_json = json.loads(f.read())
    df = pd.json_normalize(raw_json, "products", ["order_id", "warehouse_name", "highway_cost"])
    df["order_id"] = pd.to_numeric(df["order_id"], errors='coerce')
    df["highway_cost"] = pd.to_numeric(df["highway_cost"], errors='coerce')


# 1. Найти тариф стоимости доставки для каждого склада
def task_1(pd_df: DataFrame) -> DataFrame:
    pt = pd_df.pivot_table(index=["order_id", "warehouse_name"],
                           values=["highway_cost", "quantity"],
                           aggfunc={"highway_cost": "mean",
                                    "quantity": "sum"})
    pt["delivery_price"] = pt["highway_cost"] / pt["quantity"] * -1
    return pt.pivot_table(index=["warehouse_name"],
                          values=["delivery_price"])


# 2. Найти суммарное количество, суммарный доход, суммарный расход и суммарную прибыль для каждого товара
# (представить как таблицу со столбцами 'product', 'quantity', 'income', 'expenses', 'profit')
def task_2(pd_df: DataFrame) -> DataFrame:
    return get_full_table(pd_df).pivot_table(index=["product"],
                                             values=["quantity", "income", "expenses", "profit"],
                                             aggfunc="sum")


def get_full_table(pd_df: DataFrame) -> DataFrame:
    delivery_price = task_1(pd_df)
    pt = pd_df.pivot_table(index=["order_id", "warehouse_name", "product"],
                           values=["price", "quantity"],
                           aggfunc={"price": "mean",
                                    "quantity": "sum"}).join(delivery_price)
    pt["income"] = pt["price"] * pt["quantity"]
    pt["expenses"] = pt["delivery_price"] * pt["quantity"]
    pt["profit"] = pt["income"] - pt["expenses"]
    return pt


# 3. Составить табличку со столбцами 'order_id' (id заказа) и 'order_profit' (прибыль полученная с заказа).
# А также вывести среднюю прибыль заказов
def task_3(pd_df: DataFrame) -> (DataFrame, float):
    pt = get_full_table(pd_df).pivot_table(index=["order_id"],
                                           values=["profit"],
                                           aggfunc="sum")
    mean_profit = pt.mean()
    return pt, mean_profit


# 4. Составить табличку типа 'warehouse_name' , 'product','quantity', 'profit', 'percent_profit_product_of_warehouse'
# (процент прибыли продукта заказанного из определенного склада к прибыли этого склада)
def task_4(pd_df: DataFrame) -> DataFrame:
    pt = get_full_table(pd_df).pivot_table(index=["warehouse_name", "product"],
                                           values=["quantity", "profit"],
                                           aggfunc="sum")
    full_profit = pt.pivot_table(index=["warehouse_name"],
                                 values=["profit"],
                                 aggfunc="sum")
    full_profit.rename(columns={"profit": "sum_profit"}, inplace=True)
    pt = pt.join(full_profit)
    pt["percent_profit_product_of_warehouse"] = pt["profit"] / pt["sum_profit"] * 100
    return pt.drop(columns=["sum_profit"])


# 5. Взять предыдущую табличку и отсортировать 'percent_profit_product_of_warehouse' по убыванию, после
# посчитать накопленный процент. Накопленный процент - это новый столбец в этой табличке, который должен называться
# 'accumulated_percent_profit_product_of_warehouse'. По своей сути это постоянно растущая сумма отсортированного
# по убыванию столбца 'percent_profit_product_of_warehouse'.
def task_5(pd_df: DataFrame) -> DataFrame:
    pt = task_4(pd_df).sort_values(
        ["warehouse_name", "percent_profit_product_of_warehouse"], ascending=False)
    pt["accumulated_percent_profit_product_of_warehouse"] = pt.groupby(
        ["warehouse_name"])["percent_profit_product_of_warehouse"].cumsum()
    return pt


# 6. Присвоить A, B, C - категории на основании значения накопленного процента
# ('accumulated_percent_profit_product_of_warehouse'). Если значение накопленного процента меньше или равно 70,
# то категория A. Если от 70 до 90 (включая 90), то категория Б. Остальное - категория C. Новый столбец обозначить
# в таблице как 'category'
def task_6(pd_df: DataFrame) -> DataFrame:
    def set_category(row):
        name_column = "accumulated_percent_profit_product_of_warehouse"
        if row[name_column] <= 70:
            val = "A"
        elif row[name_column] <= 90:
            val = "B"
        else:
            val = "C"
        return val
    pt = task_5(pd_df)
    pt["category"] = pt.apply(set_category, axis=1)
    return pt


if __name__ == '__main__':
    cm = input("Введите номер задачи (1-6): ")
    while cm != "exit":
        match cm:
            case "1":
                print(task_1(df))
            case "2":
                print(task_2(df))
            case "3":
                table, profit = task_3(df)
                print(table)
                print("--- Средняя прибыль заказов --- ")
                print(profit)
            case "4":
                print(task_4(df))
            case "5":
                print(task_5(df))
            case "6":
                print(task_6(df))
            case _:
                print("Неверный номер")
        cm = input("Введите номер задачи (1-6), либо 'exit' для остановки: ")
