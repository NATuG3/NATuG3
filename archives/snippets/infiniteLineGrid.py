for i in range(self.domain_count + 1):
    main_plot.addItem(pg.InfiniteLine(pos=i))

twist_height = self.base_height * 21
for i in range(10):
    main_plot.addItem(pg.InfiniteLine(pos=i * twist_height, angle=0))
