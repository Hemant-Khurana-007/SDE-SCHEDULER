from bs4 import BeautifulSoup
import pandas as pd
count=0
data = {"name":[],"diff":[],"link":[],"stat":[]}
easy = {"name":[],"diff":[],"link":[],"stat":[]}
med = {"name":[],"diff":[],"link":[],"stat":[]}
hard = {"name":[],"diff":[],"link":[],"stat":[]}
with open("./webscrape/SDE.html","r") as f:
    html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all('table',class_="table-auto w-full font-dmSans divide-y divide-gray-200 dark:divide-[#363636] rounded-xl")
    for table in tables:
        rows = table.find_all("tr",class_="border-t-2 border-b-2 last:border-b-0 bg-white dark:border-dark_40 dark:bg-[#252629]")
        for row in rows:
            count+=1
            name = row.find("td",class_="px-4 py-4 w-[25%] text-left")
            diff = row.find("td",class_="px-4 py-4 w-[10%] text-sm text-center")
            nm = name.find("a")
            name2 = nm.get_text()
            dif = diff.get_text().strip()
            links = row.find("a",string="Solve")
            if dif =="":
                dif = "Hard"
            try:
                link = links.get("href")
            except:
                leettag = row.find("td",class_="px-4 py-4")
                link2 = leettag.find("a")
                link = link2.get("href")
            finally:
                data["name"].append(name2)
                data["diff"].append(dif)
                data["link"].append(link)
                data["stat"].append(0)
                if dif=="Easy":
                    easy["name"].append(name2)
                    easy["diff"].append(dif)
                    easy["link"].append(link)
                    easy["stat"].append(0)
                if dif=="Medium":
                    med["name"].append(name2)
                    med["diff"].append(dif)
                    med["link"].append(link)
                    med["stat"].append(0)
                if dif=="Hard":
                    hard["name"].append(name2)
                    hard["diff"].append(dif)
                    hard["link"].append(link)
                    hard["stat"].append(0)
   
    print(count)
    df = pd.DataFrame(data)
    df.to_csv(r".\dataset.csv", index=False)
    df = pd.DataFrame(easy)
    df.to_csv(r".\easy.csv", index=False)
    df = pd.DataFrame(med)
    df.to_csv(r".\med.csv", index=False)
    df = pd.DataFrame(hard)
    df.to_csv(r".\hard.csv", index=False)

    