import math

class VectorValueError( ValueError ):
	pass

class Vector:
	def __init__( self, x, y ):
		self.x = float( x )
		self.y = float( y )
	def __str__( self ):
		return '(' + str(self.x) + ', ' + str(self.y) + ')'
	def __add__( self, other ):
		return Vector( self.x + other.x, self.y + other.y )
	def __sub__( self, other ):
		return Vector( self.x - other.x, self.y - other.y )
	def __eq__( self, other ):
		return ( self.x == other.x ) and ( self.y == other.y )
	def __ne__( self, other ):
		return not self == other
	def __hash__( self ):
		return hash( (self.x, self.y) )

#Computationally faster than (vector.length()**2)
def lengthSquared( v ):
	return dot( v, v )
def length( v ):
	return math.sqrt( lengthSquared( v ) )

def norm( v ):
	if v == Vector( 0, 0, 0 ):
		raise VectorValueError("Tried to normalize ( 0, 0, 0 ).")
	return scale( 1.0 / length( v ), v )

def dot( v, w ):
	return v.x * w.x + v.y * w.y

def scale( n, v ):
	return Vector( n * v.x, n * v.y )

#NOTE THIS IS IN SIMULATOR SPACE
def unitVector( theta ):
    return Vector( math.sin( theta ), math.cos( theta ) )
