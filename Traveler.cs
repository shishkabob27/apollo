using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;

public class Traveler : Entity
{
    public override string TextureName => "traveler/traveler_2";
    public override bool Colidable => false;


    public Color[] Colors = {
        Color.Red,
        Color.Green,
        Color.Blue,
        Color.Yellow,
        Color.Purple,
        Color.Orange,
        Color.Pink,
        Color.Brown,
        Color.White,
        Color.Gray,
        Color.Cyan,
        Color.Magenta,
        Color.Lime,
        Color.Turquoise
    };

    public Traveler()
	{
        Color = Colors[new Random().Next(0, Colors.Length)];
	}

    public override void Tick()
    {
        base.Tick();

        Wander();

        SetTexture("traveler/traveler_" + Direction.ToString() );
    }

    public void Wander()
    {
        if (new Random().Next(0, 50) == 0)
        {
            Direction = new Random().Next(0, 4);
        }
        Move();
    }

    public void Move(){
        if (Direction == 0)
        {
            Position.Y -= Speed;
        }
        else if (Direction == 1)
        {
            Position.X += Speed;
        }
        else if (Direction == 2)
        {
            Position.Y += Speed;
        }
        else if (Direction == 3)
        {
            Position.X -= Speed;
        }

        if (Position.X < 0)
        {
            Position.X = 0;
            Direction = 1;
        }
        if (Position.Y < 0)
        {
            Position.Y = 0;
            Direction = 2;
        }
        if (Position.X > StellerFuseGame.Current.Frame.Size.X - Size.X)
        {
            Position.X = StellerFuseGame.Current.Frame.Size.X - Size.X;
            Direction = 3;
        }
        if (Position.Y > StellerFuseGame.Current.Frame.Size.Y - Size.Y)
        {
            Position.Y = StellerFuseGame.Current.Frame.Size.Y - Size.Y;
            Direction = 0;
        }

        //check if entity is colliding with another entity
        foreach (Entity entity in StellerFuseGame.Current.Frame.Entities.ToArray())
        {
            if (entity.Colidable && entity != this)
            {
                if (Position.X < entity.Position.X + entity.Size.X && Position.X + Size.X > entity.Position.X && Position.Y < entity.Position.Y + entity.Size.Y && Position.Y + Size.Y > entity.Position.Y)
                {
                    if (Direction == 0)
                    {
                        Position.Y += Speed;
                        Direction = 2;
                    }
                    else if (Direction == 1)
                    {
                        Position.X -= Speed;
                        Direction = 3;
                    }
                    else if (Direction == 2)
                    {
                        Position.Y -= Speed;
                        Direction = 0;
                    }
                    else if (Direction == 3)
                    {
                        Position.X += Speed;
                        Direction = 1;
                    }
                }
            }
        }
    }

}
