using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;
using System.Collections.Generic;

public class Frame
{

	public List<Entity> Entities = new List<Entity>();
	public Vector2 Size = new Vector2(2048, 2048);
	public Camera Camera = new Camera();

    public Frame()
	{

	}

	public virtual void Update(GameTime gameTime)
	{
		foreach (Entity entity in Entities)
		{
			entity.Update(gameTime);
		}
    }

	public virtual void Tick()
	{
		foreach (Entity entity in Entities)
		{
			entity.Tick();
		}
    }

	public virtual void Draw()
	{
		foreach (Entity entity in Entities)
		{
			  entity.Draw();
		}

    }

	public Entity AddEntity(Entity entity)
	{
		Entities.Add(entity);

		return entity;
    }

	public void RemoveEntity(Entity entity)
	{
		Entities.Remove(entity);
	}

}
