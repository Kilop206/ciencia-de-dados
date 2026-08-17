import pandas as pd

df = pd.DataFrame({
    "nome": ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo"],
    "idade": [17, 18, 19, 17, 20],
    "nota": [8.5, 6.0, 9.5, 7.0, 5.5]
})

print(df[df["nota"] > 7])
print()
print(df[df["nota"] < 7])
print()
print(df[df["nota"].max()])
print()
print(df["nota"].mean())
print()
df["aprovado"] = df["nota"] >= 7
print(df[df["aprovado"]])
print()
print(df.sort_values(by="nota", ascending=False))
print()