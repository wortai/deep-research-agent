const RichResponse = () => {
  return (
    <article className="rich-text">
      <h1>The Silicon Arms Race: Blackwell vs. WSE-3</h1>
      <p>
        The transition to trillion-parameter models has moved the bottleneck from pure compute to
        interconnect bandwidth and memory latency. Our deep-scan of technical whitepapers reveals a
        diverging philosophy between Nvidia's modular approach and Cerebras' monolithic wafer-scale
        integration.
      </p>

      <h2>Nvidia Blackwell (B200) Efficiency Metrics</h2>
      <p>
        Nvidia's Blackwell architecture leverages a dual-die design connected via a 10TB/s
        high-speed link. This effectively functions as a single GPU to the programmer while allowing
        for yields that would be impossible for a single die of that size. The inclusion of a
        second-generation transformer engine specifically optimized for FP4 precision allows for a
        theoretical 5x increase in training throughput compared to Hopper.
      </p>

      <div className="my-8 border-l-4 border-coral pl-6 italic text-xl text-primary opacity-80">
        "The core constraint for LLM training in 2025 will not be the chip, but the power density
        required to cool the interconnect fabric between clusters."
      </div>

      <h2>Cerebras WSE-3: The Wafer Scale Advantage</h2>
      <p>
        Cerebras continues its 'One Chip, One Wafer' strategy. By keeping all compute and memory on
        a single piece of silicon, they bypass the traditional bottleneck of off-chip communication
        entirely. For models that fit within its 44GB of on-chip SRAM, training speed is an order of
        magnitude faster than a cluster of 8x GPUs.
      </p>

      <div className="my-8">
        <img
          src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=1200"
          alt="Semiconductor Micrograph"
          className="w-full aspect-video object-cover grayscale"
        />
        <p className="font-mono text-[10px] opacity-40 mt-2 uppercase tracking-tighter text-right">
          Fig 1.1: SEMICONDUCTOR_TOPOLOGY_MAP // SOURCE: WORT_DATABASE
        </p>
      </div>

      <p>
        In summary, Nvidia remains the versatile choice for multi-tenant cloud providers, while
        Cerebras offers an unparalleled performance-per-kilowatt for specialized large-scale research
        labs focused on singular foundational models.
      </p>
    </article>
  );
};

export default RichResponse;
