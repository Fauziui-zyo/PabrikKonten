import json, csv

def run():
    with open("state.json", "r") as f: data = json.load(f)
    with open('metadata.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Filename', 'Title', 'Keywords'])
        writer.writerow(['base_image.jpg', data['adobestock']['judul'], data['adobestock']['kata_kunci']])
    print("Fase 3 Sukses.")

if __name__ == "__main__": run()
