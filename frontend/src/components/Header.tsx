import Image from 'next/image'

export default function Header() {
  return (
    <div className="w-full h-20 px-6 flex items-center justify-between" style={{ backgroundColor: '#1A1A1A' }}>
      {/* Left: Logo + App Name */}
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 relative">
          <Image 
            src="/verityn-logo.png"
            alt="Verityn AI Logo" 
            width={48}
            height={48}
            className="rounded-lg"
          />
        </div>
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
      
      {/* Right: Demo Mode */}
      <div className="text-right">
        <p className="text-sm font-medium" style={{ color: '#E0E0E0' }}>Demo Mode</p>
        <p className="text-xs" style={{ color: '#A0A0A0' }}>Prototype Version</p>
      </div>
    </div>
  )
} 