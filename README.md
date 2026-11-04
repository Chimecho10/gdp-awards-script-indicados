https://fonts.google.com/specimen/Cinzel
mkdir -p ~/.local/share/fonts
cp ~/Downloads/Cinzel/*.ttf ~/.local/share/fonts/
fc-cache -f -v
fc-match "Cinzel"
Deve aparecer: Cinzel-Regular.ttf: "Cinzel" "Regular"