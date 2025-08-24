import logo from 'figma:asset/306e1b4c6686df4a8e4b02992619daa100fad23b.png';

export function TopBanner() {
  return (
    <div className="w-full h-20 px-6 flex items-center justify-between" style={{ backgroundColor: '#1A1A1A' }}>
      {/* Left: Logo + App Name */}
      <div className="flex items-center gap-4">
        <img src={logo} alt="Verityn AI Logo" className="w-12 h-12" />
        <h1 
          className="text-2xl font-semibold bg-gradient-to-r from-[#9600FF] to-[#7C3AED] bg-clip-text text-transparent"
        >
          Verityn AI
        </h1>
      </div>
      
      {/* Center: Tagline */}
      <div className="flex-1 text-center">
        <p className="text-lg" style={{ color: '#E0E0E0' }}>
          Intelligent Compliance & Document Analysis
        </p>
      </div>
      
      {/* Right: Space for future elements */}
      <div className="w-32"></div>
    </div>
  );
}