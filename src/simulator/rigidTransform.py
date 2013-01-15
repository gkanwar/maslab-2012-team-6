from vector import *
from math import *

class RigidTransform:
	def __init__( self, offset, rotation ):
		self.offset = offset
		self.rotation = rotation
	def __str__( self ):
		return "A rotation of " + str( self.rotation / pi ) + "*pi radians widdershins followed by an offset of " + str( self.offset ) + " units ( length " + str( length( self.offset ) ) +" )."
	def __mul__( self, other ):
		if isinstance( other, RigidTransform ):
			rotation = self.rotation + other.rotation
			while rotation < 0:
				rotation += 2 * pi
			while rotation >= 2 * pi:
				rotation -= 2 * pi
			return RigidTransform( self.offset + self * other.offset, rotation )
		if isinstance( other, Vector ):
			return Vector( other.x * cos( self.rotation ) - other.y * sin( self.rotation ), other.x * sin( self.rotation ) + other.y * cos( self.rotation ) ) + self.offset
	def __pow__( self, power ):
		if not isinstance( power, int ):
			raise ValueError()
		if power == 0:
			return RigidTransform( Vector(), 0 )
		if power == 1:
			return self
		if power < 0:
			return inverse( self ) ** ( power * -1 )
		while power > 1:
			return self * ( self ** ( power - 1 ) )
			
def inverse( T ):
	return RigidTransform( Vector(), -T.rotation) * RigidTransform( scale( -1, T.offset ), 0 )
	
T = RigidTransform( Vector( 0, 1 ), pi / 6 )

print T
print T * T
print T ** 12
print T ** (-1)
			

