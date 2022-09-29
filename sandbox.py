class Rec:
	RECTANGLE = 'Quadruple'
	def __init__(self, side_A, side_B):
		self.side_A = side_A
		self.side_B = side_B

	@classmethod
	def name(cls):
		return cls.RECTANGLE

	@staticmethod
	def detail():
		return('A 4-sided shape')


my_rec = Rec(2, 4)
print(my_rec.detail())
# print(my_rec)