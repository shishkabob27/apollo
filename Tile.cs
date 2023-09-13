public class Tile : Entity
{
    public virtual string Name { get; set; } = "Tile";
    public int Price { get; set; } = 500;

    public Tile()
    {
        SetTexture("tile/wall");
    }

}

public class Wall : Tile
{
    public override string Name { get; set; } = "Wall";
    public override bool Colidable { get; set; } = true;
    public override int Layer { get; set; } = 1;

    public Wall()
    {
        SetTexture("tile/wall");
    }

}

public class Floor : Tile
{
    public override string Name { get; set; } = "Floor";
    public override bool Colidable { get; set; } = false;
    public override int Layer { get; set; } = 0;

    public Floor()
    {
        SetTexture("tile/floor");
    }

}