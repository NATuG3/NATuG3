import dna_nanotube_tools

m_c = [6, 7, 7, 7, 7, 7, 7, 0, 0, 0]
m_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
generated_top_view = dna_nanotube_tools.top_view(m_c, m_s, 2.3)

cords = generated_top_view.cords()
cords = [(round(u, 2), round(v, 2)) for u, v in cords]

print(cords)