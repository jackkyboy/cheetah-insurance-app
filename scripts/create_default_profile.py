from PIL import Image, ImageDraw

# กำหนดขนาดรูปภาพ
size = (200, 200)

# สร้างภาพพื้นหลังสีขาว
image = Image.new("RGB", size, "white")

# วาดวงกลมตรงกลาง
draw = ImageDraw.Draw(image)
circle_color = (200, 200, 200)  # สีเทา
circle_radius = 90  # รัศมีวงกลม
center = (size[0] // 2, size[1] // 2)

# สร้างวงกลม
draw.ellipse(
    [center[0] - circle_radius, center[1] - circle_radius,
     center[0] + circle_radius, center[1] + circle_radius],
    fill=circle_color
)

# บันทึกไฟล์
output_path = "/Users/apichet/Downloads/cheetah-insurance-app/public/images/default-profile.png"
image.save(output_path)

print(f"✅ Default profile picture created at: {output_path}")

