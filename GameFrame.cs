using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;

public class GameFrame : Frame
{
	public GameFrame()
	{
		for (int i = 0; i < 100; i++)
		{
			var traveler = AddEntity(new Traveler());
			traveler.Position = new Vector2(new Random().Next(0, (int)Size.X), new Random().Next(0, (int)Size.Y));
		}
		
	}

    public override void Tick()
    {
        base.Tick();

		var cameraspeed = 4;
		if (Keyboard.GetState().IsKeyDown(Keys.LeftShift))
		{
			cameraspeed = 8;
		}
		if (Keyboard.GetState().IsKeyDown(Keys.W))
		{
			Camera.Position.Y -= cameraspeed;
		}
		if (Keyboard.GetState().IsKeyDown(Keys.A))
		{
			Camera.Position.X -= cameraspeed;
		}
		if (Keyboard.GetState().IsKeyDown(Keys.S))
		{
			Camera.Position.Y += cameraspeed;
		}
		if (Keyboard.GetState().IsKeyDown(Keys.D))
		{
			Camera.Position.X += cameraspeed;
		}

		Camera.PositionCheck();
    }

	public override void Update(GameTime gameTime)
	{
		if (Mouse.GetState().LeftButton == ButtonState.Pressed)
		{
			var mousePosition = new Vector2(Mouse.GetState().Position.X + Camera.Position.X, Mouse.GetState().Position.Y + Camera.Position.Y);
			var tilePosition = new Vector2((int)(mousePosition.X / 32) * 32, (int)(mousePosition.Y / 32) * 32);

			var tileOccupied = false;
			foreach (Entity entity in Entities.ToArray())
			{
				if (tilePosition.X + 32 > entity.Position.X && tilePosition.X < entity.Position.X + entity.Size.X && tilePosition.Y + 32 > entity.Position.Y && tilePosition.Y < entity.Position.Y + entity.Size.Y)
				{
					tileOccupied = true;
					break;
				}
			}

			if (!tileOccupied)
			{
				var tile = AddEntity(new Tile());
				tile.Position = tilePosition;
			}
			
		}
	}

    public override void Draw()
	{
		StellerFuseGame.Current.SpriteBatch.Draw(StellerFuseGame.Current.Content.Load<Texture2D>("background_grass"), -Camera.Position, Color.White);

		//render tile placer	
		var mousePosition = new Vector2(Mouse.GetState().Position.X + Camera.Position.X, Mouse.GetState().Position.Y + Camera.Position.Y);
		var tilePosition = new Vector2((int)(mousePosition.X / 32) * 32, (int)(mousePosition.Y / 32) * 32);
		StellerFuseGame.Current.SpriteBatch.Draw(StellerFuseGame.Current.Content.Load<Texture2D>("select_build"), tilePosition - Camera.Position, Color.White);

		base.Draw();
	}
}
