from PIL import Image, ImageDraw, ImageFont
import emoji

def generate_image_nominees(nominees, path):
    image_nom = Image.open("image_template.png")
    draw_nom = ImageDraw.Draw(image_nom)
    font_nom = ImageFont.truetype('fonte.ttf', 200)
    x_nom = image_nom.width
    y_nom = image_nom.height

    draw_nom.text(
               (x_nom//2,y_nom//2), 
                "GDP AWARDS 2026\nINDICADOS", 
                font=font_nom, 
                fill=(255,255,255),
                anchor="mm",
                align='center'
            )

    image_nom.save(f"{path}/category_{0}.png")

    for i, category in enumerate(nominees):
        image = Image.open("image_template.png")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('fonte.ttf', 100)
        font_nominees = ImageFont.truetype('fonte.ttf', 80)

        x = image.width
        y = image.height

        treated_text = emoji.replace_emoji(category.upper(), replace='').strip()

        draw.text((x//2,y//5.5), 
                   treated_text, 
                   font=font, 
                   fill=(255,255,255),
                   anchor="mm"
                   )

        draw.text((x//2,y//3.8), 
                  "INDICADOS",  
                  font=font_nominees, 
                  fill=(255,255,255),
                  anchor="mm"
                  )

        print(category)

        nominees_list = []
        for nom in nominees[category]:
            nominees_list.append(nom[0])

        nominees_list.sort()
        
        x_nominees = x//2
        num_nominees = len(nominees_list)
        if num_nominees == 5:
            count = 100
        elif num_nominees == 4:
            count = 50
        else:
            count = 0

        x_nominees = x//2
        y_nominees = y//2 - count 

        for j, nom in enumerate(nominees_list):
            draw.text(
                    (x_nominees , y_nominees + (j*100)), 
                    nom.upper(),  
                    font=font_nominees, 
                    fill=(255,255,255),
                    anchor="mm"
                    )

        image.save(f"{path}/category_{i+1}.png")