using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using MLEM;
using MLEM.Font;
using MLEM.Textures;
using MLEM.Ui;
using MLEM.Ui.Elements;
using MLEM.Ui.Style;
using System;


public class StellerFuseGame : Game
{
    public static StellerFuseGame Current;

    public GraphicsDeviceManager Graphics;
    public SpriteBatch SpriteBatch;

    public UiSystem UiSystem;

    public Frame Frame;

    int tickRate = 60;
    public Vector2 ScreenSize = new Vector2(640, 360);

    private TimeSpan lastTick = TimeSpan.Zero;
    public StellerFuseGame()
    {
        Current = this;
        Graphics = new GraphicsDeviceManager(this)
        {
            PreferredBackBufferWidth = (int)ScreenSize.X,
            PreferredBackBufferHeight = (int)ScreenSize.Y

        };
        Graphics.ApplyChanges();
        Content.RootDirectory = "Content";
        IsMouseVisible = true;
        IsFixedTimeStep = false;
    }

    protected override void Initialize()
    {
        Frame = new GameFrame();

        base.Initialize();
    }

    protected override void LoadContent()
    {
        SpriteBatch = new SpriteBatch(GraphicsDevice);

        // Initialize the Ui system
        var style = new UntexturedStyle(this.SpriteBatch) {
            Font = new GenericSpriteFont(this.Content.Load<SpriteFont>("sserife")),
            ButtonTexture = new NinePatch(this.Content.Load<Texture2D>("missing"), padding: 1)
        };


        UiSystem = new UiSystem(this, style);
    }

    protected override void Update(GameTime gameTime)
    {
        if (GamePad.GetState(PlayerIndex.One).Buttons.Back == ButtonState.Pressed || Keyboard.GetState().IsKeyDown(Keys.Escape))
            Exit();

        if (Frame != null)
        {
            Frame.Update(gameTime);

            //Tick
            if (gameTime.TotalGameTime - lastTick > TimeSpan.FromSeconds(1.0 / tickRate))
            {
                Frame.Tick();
                lastTick = gameTime.TotalGameTime;
            }
        }

        UiSystem.Update(gameTime);

        base.Update(gameTime);
    }

    protected override void Draw(GameTime gameTime)
    {
        GraphicsDevice.Clear(Color.Black);

        SpriteBatch.Begin();
            
        if (Frame != null)
            Frame.Draw();

        //draw fps
        SpriteBatch.DrawString(Content.Load<SpriteFont>("sserife"), "FPS: " + (int)(1 / gameTime.ElapsedGameTime.TotalSeconds), new Vector2(0, 0), Color.White);
        
        SpriteBatch.End();
        UiSystem.Draw(gameTime, SpriteBatch);
        base.Draw(gameTime);
    }
}