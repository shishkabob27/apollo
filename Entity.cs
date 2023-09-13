using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;

public class Entity
{
    public virtual int MaxHealth { get; set; } = 100;
    public virtual int Health { get; set; } = 100;
    public virtual int Speed { get; set; } = 1;
    public Vector2 Position = Vector2.Zero;
    public virtual Vector2 Size { get; set; } = new Vector2(32, 32);
    public int Direction = 0;
    public virtual int Layer { get; set; } = 0;
    public virtual bool Colidable { get; set; } = true;
    public virtual Color Color { get; set; } = Color.White;
    public virtual string TextureName { get; set; } = "missing";
    public Texture2D Texture { get; set; } = null;

	public Entity()
	{
        SetTexture(TextureName);
	}

    public virtual void Update(GameTime gameTime)
    {

    }

    public virtual void Tick()
    {

    }

    public virtual void Draw()
    {
        if (Texture == null)
            return;
        StellerFuseGame.Current.SpriteBatch.Draw(Texture, Position - StellerFuseGame.Current.Frame.Camera.Position, Color);
    }

    public void SetTexture(string textureName)
    {
        TextureName = textureName;
        Texture = StellerFuseGame.Current.Content.Load<Texture2D>(textureName);
    }

    public bool IsMouseHovering()
    {
         var mousePosition = new Vector2(Mouse.GetState().Position.X, Mouse.GetState().Position.Y);
        if (mousePosition.X > Position.X && mousePosition.X < Position.X + Size.X && mousePosition.Y > Position.Y && mousePosition.Y < Position.Y + Size.Y)
        {
            return true;
        }
        return false;
    }

}
