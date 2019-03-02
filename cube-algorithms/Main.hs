module Main where
import Data.Bits


data Axis            = Axis Int         deriving (Show)
data Direction       = Direction Int    deriving (Show)
data PlaneIndex      = Plane Int        deriving (Show)
data VertexIndex     = Vertex Int       deriving (Show)
data EdgeIndex       = Edge Int         deriving (Show)

plane :: Axis -> Direction -> PlaneIndex
plane (Axis axis) (Direction dir) = Plane $ axis * 2 + dir

axis :: PlaneIndex -> Axis
axis (Plane plane) = Axis $ plane `div` 2

direction :: PlaneIndex -> Direction
direction (Plane plane) = Direction $ plane `mod` 2

axes :: [Axis]
axes = map Axis [ 0, 1, 2 ]

directions :: [Direction]
directions = map Direction [ 0, 1 ]

planes :: [PlaneIndex]
planes = map Plane [ 0, 1, 2, 3, 4, 5 ]

nextAxis :: Axis -> Axis
nextAxis (Axis ax) = Axis $ (ax + 1) `mod` 3

nextDir :: Direction -> Direction
nextDir (Direction dir) = Direction $ (dir + 1) `mod` 2

vcoord :: PlaneIndex -> Int
vcoord p = coord (axis p) (direction p)
    where
        coord :: Axis -> Direction -> Int
        coord (Axis ax) (Direction d) = shiftL d ax

vindex :: PlaneIndex -> PlaneIndex -> PlaneIndex -> VertexIndex
vindex p0 p1 p2 = Vertex $ c0 + c1 + c2
    where 
        c0 = vcoord p0
        c1 = vcoord p1
        c2 = vcoord p2

vindices :: PlaneIndex -> [VertexIndex]
vindices p0 = [ 
    (vindex p0 (plane a1 d1) (plane a2 d2)) | 
        d1 <- directions,
        d2 <- directions ]
    where
        a1 = nextAxis $ axis p0
        a2 = nextAxis a1

data Vertex = Point Double Double Double
instance Show Vertex where
    show (Point x y z) = "(" ++ (show x) ++ ", " ++ (show y) ++ ", " ++ (show z) ++ ")"

vertex :: VertexIndex -> Vertex
vertex (Vertex n) = Point x y z
    where
        x = sign $ getbit 0
        y = sign $ getbit 1
        z = sign $ getbit 2
        getbit i = 1 .&. (shiftR n i)
        sign 0 = -1.0
        sign 1 = 1.0

vertices :: PlaneIndex -> [Vertex]
vertices plane = map vertex $ vindices plane


main :: IO ()
main = do
    print $ planes
    print $ map vertices planes
    print $ Plane 0
    print $ vindices $ Plane 0
    print $ vindices $ Plane 1
    print $ vindices $ Plane 2
    print $ vindices $ Plane 3
    print $ vindices $ Plane 4
    print $ vindices $ Plane 5
    print $ vindices $ Plane 6

    print $ vertices $ Plane 0
    print $ vertices $ Plane 1
    print $ vertices $ Plane 2
    print $ vertices $ Plane 3
    print $ vertices $ Plane 4
    print $ vertices $ Plane 5
    print $ vertices $ Plane 6
