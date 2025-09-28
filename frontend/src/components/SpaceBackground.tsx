'use client';

import React from 'react';
import styles from './SpaceBackground.module.css';

export default function SpaceBackground() {
  return (
    <div className={styles.spaceBackground}>
      <svg className={styles.spaceSvg} viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
        {/* Animated Stars - More Natural Distribution */}
        <g className={styles.stars}>
          <circle cx="87" cy="134" r="0.8" fill="#ffffff" opacity="0.6">
            <animate attributeName="opacity" values="0.2;0.8;0.2" dur="3.1s" repeatCount="indefinite" />
          </circle>
          <circle cx="234" cy="67" r="1.1" fill="#a29bfe" opacity="0.4">
            <animate attributeName="opacity" values="0.1;0.7;0.1" dur="4.3s" repeatCount="indefinite" />
          </circle>
          <circle cx="387" cy="203" r="0.9" fill="#ffffff" opacity="0.5">
            <animate attributeName="opacity" values="0.3;0.9;0.3" dur="2.7s" repeatCount="indefinite" />
          </circle>
          <circle cx="521" cy="89" r="0.7" fill="#00b894" opacity="0.3">
            <animate attributeName="opacity" values="0.2;0.6;0.2" dur="3.8s" repeatCount="indefinite" />
          </circle>
          <circle cx="678" cy="156" r="1.2" fill="#ffffff" opacity="0.7">
            <animate attributeName="opacity" values="0.1;1;0.1" dur="4.1s" repeatCount="indefinite" />
          </circle>
          <circle cx="743" cy="298" r="0.6" fill="#6c5ce7" opacity="0.4">
            <animate attributeName="opacity" values="0.3;0.7;0.3" dur="2.9s" repeatCount="indefinite" />
          </circle>
          <circle cx="865" cy="178" r="0.9" fill="#ffffff" opacity="0.6">
            <animate attributeName="opacity" values="0.2;0.8;0.2" dur="3.4s" repeatCount="indefinite" />
          </circle>
          <circle cx="1034" cy="234" r="0.8" fill="#a29bfe" opacity="0.4">
            <animate attributeName="opacity" values="0.1;0.6;0.1" dur="3.6s" repeatCount="indefinite" />
          </circle>
          <circle cx="1187" cy="123" r="1" fill="#ffffff" opacity="0.5">
            <animate attributeName="opacity" values="0.2;0.9;0.2" dur="3.9s" repeatCount="indefinite" />
          </circle>
          <circle cx="1346" cy="267" r="0.7" fill="#00b894" opacity="0.6">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="4.2s" repeatCount="indefinite" />
          </circle>
          <circle cx="1523" cy="145" r="0.9" fill="#6c5ce7" opacity="0.4">
            <animate attributeName="opacity" values="0.2;0.7;0.2" dur="3.3s" repeatCount="indefinite" />
          </circle>
          <circle cx="1678" cy="198" r="1.1" fill="#ffffff" opacity="0.7">
            <animate attributeName="opacity" values="0.1;0.8;0.1" dur="2.8s" repeatCount="indefinite" />
          </circle>
          <circle cx="143" cy="376" r="0.6" fill="#ffffff" opacity="0.3">
            <animate attributeName="opacity" values="0.2;0.5;0.2" dur="4.5s" repeatCount="indefinite" />
          </circle>
          <circle cx="456" cy="334" r="0.8" fill="#a29bfe" opacity="0.4">
            <animate attributeName="opacity" values="0.1;0.6;0.1" dur="3.7s" repeatCount="indefinite" />
          </circle>
          <circle cx="789" cy="387" r="0.7" fill="#00b894" opacity="0.3">
            <animate attributeName="opacity" values="0.2;0.7;0.2" dur="4.0s" repeatCount="indefinite" />
          </circle>
          <circle cx="1234" cy="345" r="0.9" fill="#ffffff" opacity="0.5">
            <animate attributeName="opacity" values="0.3;0.8;0.3" dur="3.2s" repeatCount="indefinite" />
          </circle>
        </g>

        {/* Floating Particles */}
        <g className={styles.particles}>
          <circle cx="150" cy="300" r="2" fill="#6c5ce7" opacity="0.3">
            <animateTransform attributeName="transform" type="translate" values="0,0; 20,-30; 0,0" dur="8s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.1;0.5;0.1" dur="8s" repeatCount="indefinite" />
          </circle>
          <circle cx="800" cy="400" r="1.5" fill="#00b894" opacity="0.4">
            <animateTransform attributeName="transform" type="translate" values="0,0; -25,40; 0,0" dur="10s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.2;0.6;0.2" dur="10s" repeatCount="indefinite" />
          </circle>
          <circle cx="400" cy="450" r="1.8" fill="#a29bfe" opacity="0.3">
            <animateTransform attributeName="transform" type="translate" values="0,0; 30,20; 0,0" dur="12s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.1;0.4;0.1" dur="12s" repeatCount="indefinite" />
          </circle>
          <circle cx="1200" cy="250" r="1.2" fill="#ffffff" opacity="0.4">
            <animateTransform attributeName="transform" type="translate" values="0,0; -15,-25; 0,0" dur="9s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.2;0.5;0.2" dur="9s" repeatCount="indefinite" />
          </circle>
          <circle cx="600" cy="600" r="1.6" fill="#6c5ce7" opacity="0.3">
            <animateTransform attributeName="transform" type="translate" values="0,0; 35,-20; 0,0" dur="11s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.1;0.4;0.1" dur="11s" repeatCount="indefinite" />
          </circle>
          <circle cx="1000" cy="500" r="1.4" fill="#00b894" opacity="0.4">
            <animateTransform attributeName="transform" type="translate" values="0,0; -20,30; 0,0" dur="13s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.2;0.5;0.2" dur="13s" repeatCount="indefinite" />
          </circle>
        </g>

        {/* Distant Planets/Objects */}
        <g className={styles.planets}>
          <circle cx="1400" cy="120" r="8" fill="url(#planetGradient1)" opacity="0.6">
            <animateTransform attributeName="transform" type="rotate" values="0 1400 120; 360 1400 120" dur="30s" repeatCount="indefinite" />
          </circle>
          <circle cx="1600" cy="300" r="5" fill="url(#planetGradient2)" opacity="0.4">
            <animateTransform attributeName="transform" type="rotate" values="0 1600 300; -360 1600 300" dur="45s" repeatCount="indefinite" />
          </circle>
          <circle cx="80" cy="400" r="6" fill="url(#planetGradient3)" opacity="0.3">
            <animateTransform attributeName="transform" type="rotate" values="0 80 400; 360 80 400" dur="40s" repeatCount="indefinite" />
          </circle>
        </g>

        {/* Nebula-like background shapes */}
        <g className={styles.nebula}>
          <ellipse cx="300" cy="600" rx="150" ry="80" fill="url(#nebulaGradient1)" opacity="0.1">
            <animateTransform attributeName="transform" type="scale" values="1;1.2;1" dur="20s" repeatCount="indefinite" />
          </ellipse>
          <ellipse cx="1400" cy="700" rx="200" ry="100" fill="url(#nebulaGradient2)" opacity="0.08">
            <animateTransform attributeName="transform" type="scale" values="1;1.1;1" dur="25s" repeatCount="indefinite" />
          </ellipse>
        </g>

        {/* Multiple Shooting Stars */}
        <g className={styles.shootingStars}>
          <line x1="100" y1="80" x2="180" y2="120" stroke="url(#shootingStarGradient)" strokeWidth="2" opacity="0">
            <animate attributeName="opacity" values="0;1;0" dur="0.8s" begin="3s;15s;27s" />
            <animateTransform attributeName="transform" type="translate" values="0,0; 120,60; 250,130" dur="0.8s" begin="3s;15s;27s" />
          </line>
          <line x1="1200" y1="150" x2="1280" y2="190" stroke="url(#shootingStarGradient)" strokeWidth="1.5" opacity="0">
            <animate attributeName="opacity" values="0;1;0" dur="0.6s" begin="7s;19s;31s" />
            <animateTransform attributeName="transform" type="translate" values="0,0; 100,50; 200,100" dur="0.6s" begin="7s;19s;31s" />
          </line>
          <line x1="600" y1="50" x2="680" y2="90" stroke="url(#shootingStarGradient)" strokeWidth="1.8" opacity="0">
            <animate attributeName="opacity" values="0;1;0" dur="0.7s" begin="11s;23s;35s" />
            <animateTransform attributeName="transform" type="translate" values="0,0; 130,65; 260,130" dur="0.7s" begin="11s;23s;35s" />
          </line>
          <line x1="400" y1="250" x2="480" y2="290" stroke="url(#shootingStarGradient)" strokeWidth="1.2" opacity="0">
            <animate attributeName="opacity" values="0;1;0" dur="0.5s" begin="5s;17s;29s" />
            <animateTransform attributeName="transform" type="translate" values="0,0; 90,45; 180,90" dur="0.5s" begin="5s;17s;29s" />
          </line>
          <line x1="1500" y1="200" x2="1580" y2="240" stroke="url(#shootingStarGradient)" strokeWidth="1.4" opacity="0">
            <animate attributeName="opacity" values="0;1;0" dur="0.9s" begin="9s;21s;33s" />
            <animateTransform attributeName="transform" type="translate" values="0,0; 140,70; 280,140" dur="0.9s" begin="9s;21s;33s" />
          </line>
        </g>

        {/* Flying Rocket - 5x Bigger */}
        <g className={styles.rocket}>
          <g opacity="0.8">
            <animateTransform attributeName="transform" type="translate" values="100,400; 200,350; 100,400" dur="12s" repeatCount="indefinite" />
            
            {/* Rocket Body */}
            <ellipse cx="0" cy="0" rx="40" ry="125" fill="url(#rocketGradient)" />
            
            {/* Rocket Nose */}
            <circle cx="0" cy="-100" r="20" fill="#a29bfe" />
            
            {/* Rocket Fins */}
            <polygon points="-30,75 -50,125 -10,100" fill="#6c5ce7" />
            <polygon points="30,75 50,125 10,100" fill="#6c5ce7" />
            
            {/* Rocket Exhaust */}
            <ellipse cx="0" cy="150" rx="15" ry="40" fill="#ff7675" opacity="0.8">
              <animate attributeName="ry" values="40;60;40" dur="0.3s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.8;1;0.8" dur="0.2s" repeatCount="indefinite" />
            </ellipse>
            <ellipse cx="0" cy="175" rx="10" ry="30" fill="#fdcb6e" opacity="0.6">
              <animate attributeName="ry" values="30;50;30" dur="0.4s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.6;0.9;0.6" dur="0.25s" repeatCount="indefinite" />
            </ellipse>
            
            {/* Rocket Window */}
            <circle cx="0" cy="-25" r="15" fill="#00b894" opacity="0.7" />
          </g>
        </g>

        {/* Gradient Definitions */}
        <defs>
          <radialGradient id="planetGradient1" cx="0.3" cy="0.3">
            <stop offset="0%" stopColor="#6c5ce7" stopOpacity="0.8"/>
            <stop offset="100%" stopColor="#2d3436" stopOpacity="0.2"/>
          </radialGradient>
          <radialGradient id="planetGradient2" cx="0.4" cy="0.2">
            <stop offset="0%" stopColor="#00b894" stopOpacity="0.7"/>
            <stop offset="100%" stopColor="#2d3436" stopOpacity="0.1"/>
          </radialGradient>
          <radialGradient id="planetGradient3" cx="0.2" cy="0.4">
            <stop offset="0%" stopColor="#a29bfe" stopOpacity="0.6"/>
            <stop offset="100%" stopColor="#2d3436" stopOpacity="0.1"/>
          </radialGradient>
          <radialGradient id="nebulaGradient1" cx="0.5" cy="0.5">
            <stop offset="0%" stopColor="#6c5ce7" stopOpacity="0.3"/>
            <stop offset="100%" stopColor="#6c5ce7" stopOpacity="0"/>
          </radialGradient>
          <radialGradient id="nebulaGradient2" cx="0.5" cy="0.5">
            <stop offset="0%" stopColor="#00b894" stopOpacity="0.25"/>
            <stop offset="100%" stopColor="#00b894" stopOpacity="0"/>
          </radialGradient>
          <linearGradient id="shootingStarGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0"/>
            <stop offset="50%" stopColor="#ffffff" stopOpacity="1"/>
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0"/>
          </linearGradient>
          <linearGradient id="rocketGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#74b9ff" stopOpacity="1"/>
            <stop offset="50%" stopColor="#0984e3" stopOpacity="1"/>
            <stop offset="100%" stopColor="#2d3436" stopOpacity="0.8"/>
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}
