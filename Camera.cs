using System;
using Microsoft.Xna.Framework;

public class Camera : Entity
{

    public Camera()
    {
        Position = new Vector2(0, 0);
    }

    public void PositionCheck()
    {
        if (Position.X < 0)
        {
            Position.X = 0;
        }
        if (Position.Y < 0)
        {
            Position.Y = 0;
        }
        if (Position.X > StellerFuseGame.Current.Frame.Size.X - StellerFuseGame.Current.ScreenSize.X)
        {
            Position.X = StellerFuseGame.Current.Frame.Size.X - StellerFuseGame.Current.ScreenSize.X;
        }
        if (Position.Y > StellerFuseGame.Current.Frame.Size.Y - StellerFuseGame.Current.ScreenSize.Y)
        {
            Position.Y = StellerFuseGame.Current.Frame.Size.Y - StellerFuseGame.Current.ScreenSize.Y;
        }
    }
    
}