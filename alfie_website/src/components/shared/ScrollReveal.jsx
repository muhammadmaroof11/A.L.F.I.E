import React, { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollReveal({ 
  children, 
  y = 30, 
  duration = 0.8, 
  delay = 0, 
  stagger = 0, 
  className = "" 
}) {
  const elRef = useRef(null);

  useEffect(() => {
    const el = elRef.current;
    if (!el) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        el,
        { opacity: 0, y: y },
        {
          opacity: 1,
          y: 0,
          duration: duration,
          delay: delay,
          stagger: stagger,
          ease: 'power3.out',
          clearProps: 'transform',
          scrollTrigger: {
            trigger: el,
            start: 'top 88%',
            toggleActions: 'play none none none',
          },
        }
      );
    }, elRef);

    return () => ctx.revert();
  }, [y, duration, delay, stagger]);

  return (
    <div ref={elRef} className={className}>
      {children}
    </div>
  );
}
