from PIL import Image, ImageDraw, ImageFont
import os
import cv2


def add_filename_to_image(image_path, output_path):
    # Open the original image
    image = Image.open(image_path)
    width, height = image.size

    # Define the new width and height (original height + space for text)
    test_size = 38
    line_height = 45
    new_height = height + line_height  # Adjust this value based on your needs
    new_image = Image.new(
        "RGB", (width, new_height), (150, 150, 150)
    )  # White background

    new_image.paste(image, (0, 0))

    # Prepare to draw text
    draw = ImageDraw.Draw(new_image)

    font_path = os.path.join(cv2.__path__[0], "qt", "fonts", "DejaVuSans.ttf")
    font = ImageFont.truetype(font_path, size=38)
    # font = ImageFont.load_default(size=test_size)  # You can use a different font here

    # Define the text position
    text = os.path.basename(image_path)
    text_x = test_size
    text_y = height  # Adjust this value based on your needs

    # Draw the text onto the image
    draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)  # Black text

    # Save the new image
    new_image.save(output_path)


if __name__ == "__main__":
    paths = [
        "/mnt/mechanical/resource/17doc/zhangwanying/",
    ]
    for path in paths:
        path += "thumbnails/"
        for file in os.listdir(path):
            add_filename_to_image(path + file, path + file)
            print(path + file)
            # exit()
