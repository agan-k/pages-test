\version "2.24.4"
\language "english"

% 1. Define the custom text appearance for the chord exception
halfDiminishedException = {
  <c ef gf bf>-\markup { "m" \super "7 " \super \flat \super "5" }
}

% 2. Merge new formatting style into LilyPond's internal exception table
chdefs = #(append 
           (sequential-music-to-chord-exceptions halfDiminishedException #t) 
           ignatzekExceptions)

\paper {
  system-system-spacing = #'(
    (basic-distance . 15)
    (minimum-distance . 10)
    (padding . 2)
    (stretchability . 60)
  )
  page-breaking = #ly:one-page-breaking
}

\header {
  title = "How Deep Is The Ocean"
  subsubtitle = "Miles Davis solo"
  tagline = ##f
}

ending = {
  \new StaffGroup {
     <<
       \chords {
         \set majorSevenSymbol = \markup { maj7 }
         \set noChordSymbol = ""
         r8 f:maj7 ef:maj7 df:maj7 f2:6.9 |
       }
       \new Staff {        
          \override Staff.VerticalAxisGroup.staff-staff-spacing =
              #'( (basic-distance . 5) 
                  (minimum-distance . 5) 
                  (padding . 1) )
          \override Staff.Clef.stencil = ##f
          \override Staff.TimeSignature.stencil = ##f
          \override Staff.BarLine.stencil = ##f
          \override Staff.StaffSymbol.line-count = #0
          \improvisationOn r8 d''8 d''8 d''8 d''2 |
       }
     >>
   }
}

\score {
 <<
   <<
     \chords {
       \set chordNameExceptions = #chdefs
       \set chordChanges = ##t % overrides printing if same chord next measure.
       \set majorSevenSymbol = \markup { maj7 }
       a2.:7.9+ |
       %Chorus 1/2
       % A section
       d1:m | a:aug7 | d:m | b2:m7.5- e:7.9- | 
       a1:m | b2:m7.5- e:7.9- | a:m7 af:13 | g:m7 c:7 |
       f1:13.9- | f1:13.9- | bf:7.5- | bf:7.5- |
       df:7.5- | df:7.5- | c:aug7 | a:aug7 \bar "||"
       % B section
       \tweak X-offset #1 d1:m | a:aug7 | d:m | b2:m7.5- e:7.9- | 
       a1:m | b2:m7.5- e:7.9- | a:m7 af:13 | g:m7 c:7 |
       a1:m7.5- | d:7.9- | g:m7 | bf:m6 |
       f:maj7 | g:7 | g2:m7 c2:7 | e:m7.5- a:aug7 \bar "||"
       %Chorus 2/2
       % A section
       d1:m | a:aug7 | d:m | b2:m7.5- e:7.9- | 
       a1:m | b2:m7.5- e:7.9- | a:m7 af:13 | g:m7 c:7 |
       f1:13.9- | f1:13.9- | bf:7.5- | bf:7.5- |
       df:7.5- | df:7.5- | c:aug7 | a:aug7 \bar "||"
       % B section
       d1:m | a:aug7 | d:m | b2:m7.5- e:7.9- | 
       a1:m | b2:m7.5- e:7.9- | a:m7 af:13 | g:m7 c:7 |
       a1:m7.5- | d:7.9- | g:m7 | bf:m6 |
       f:maj7 | g:7 | g2:m7 c2:7 |
       <<
         \ending
       >>
         
     }
   >>
   \new Staff \with {instrumentName = "Trumpet"}
     \relative c' {
       \override TupletBracket.tuplet-slur = ##t
       \override TupletBracket.bracket-visibility = ##t
       \key f \major
       % Pickup
       \partial 2. e16 f fs g c8.\fermata bf16 a g8. \bar "||"
       
       % Chorus 1/2
       % Section A
       \mark \markup { \box "A" }
       f2~ f8 f16 f f e f g | a8 a4. r2 | 
       r4 r16 a e' f d4 a16 g \tuplet 3/2 {f e f} | 
       a4~ a16 b c d e f8. e d16 | 
       
       c8 c4. r4. a32b c d | e16 c d d~ d4 r2 | 
       r4 c8 c c4. e16d | bf2 r4. f16 g | 
       
       ef2 r4 f'8 f16 f | f c8. c4~ c4. c16 c | 
       c8. bf32 a af4 r16 c, f g af bf b c |
       f c bf8~ bf8. af16 af4 \tuplet 3/2 {f16 g f} e16 f | 
       
       \tuplet 3/2 {g16 af g} gf16 f r2. | 
       r4. f16 g af16 bf g8~ g16 f e f | af8 g \tuplet 3/2 {g8 g g} g4 r4 |
       \tuplet 3/2 4 {r8 cs, ds e f g a b c cs d e}
       
       % Chorus 1/2
       % Section B
       \tweak Y-offset #-2
       \mark \markup { \box "B" }
       f2 b,16 r8. f'8 e16 d | a a8. r8 b16 cs a8 b16 cs a8 b16 cs |
       a4  r4 r4 f'8 e16 d | a4~ a16 bf c d e f g8 r8 f8~ |
       
       f e~ e d~ d b~ b c16 d | \tuplet 3/2 {\acciaccatura ds8 e8 d d~} d4 r2 |
       r4. c16 c c4~ c16 d e c | bf2 r2 |
       
       ef,4 f8 g \tuplet 3/2 4 {a bf c a bf c} |
       f4~ f16 ef d c bf a gs a d8. c16 |
       \tuplet 3/2 {a16 bf b} c16 c c8. c16 c b bf8 r8 f16 df | 
       ef2. r8 c'16 bf |
       
       a2 r4 a16 bf c d | \tuplet 3/2 {e8 f4} e4 \tuplet 3/2 {d8 c b} r4 |
       r4 d,8 g g4~ g16 a bf b | c a~ a4. df,16 ef e fs g a bf c \bar "||"
       \break
       
       % Chorus 2/2
       % Section A
       \mark \markup { \box "A" }
       cs8. b32 c a4~ a4.. a16 | b16 cs \tuplet 3/2 {b c a~} a4 r2 |
       r4 e'8 e \tuplet 3/2 4 {e e e e e e} | 
       e16 f d8~ d e16 f e8 d16 b gs f e8~ |
       
       e4 r4 r16 e16 a b c d e c | d16 b8. gs16 f e8~ e4 r4 |
       r4 c'8. a16 c4~ c16 d e c | bf4 r2 r8. f'16 |
       
       \tuplet 3/2 {ef8 fs, g} d'2 f8 f16 f | 
       f c c8~ c2 \tuplet 3/2 {c8 c c} | c8 b32 bf a af~ af4 r4 r16 c, f g | 
       af bf g af f4 r4 f32 g f e f16 g |
       
       af8 g16 gf f4 f2 | r2 r8. g16 af g f af |
       af g8.~ g2~ g16 a bf c | cs8 d e f cs4 r4 |
       
       % Chorus 2/2
       % Section B
       r4 f2 f16 f e d | \tuplet 3/2 {a8 a4~} a r2 |
       r4. a16 g \tuplet 3/2 {f8 f f~} f e16 f |
       
       g gs a bf  b8. c16 df8 \tuplet 3/2 {c16 b bf~} bf8 e16 e |
       c2 r4 c16 d e f | \tuplet 3/2 {d8 d d~} d4 r2 |
       r4 \tuplet 3/2 {r8 c c} c4~ c16 d e c |
       
       bf2 r2 | r4 f'2~ f8. e16 | ef8 d  a4 r8 gs16 a d ef r16 a, |
       \tuplet 3/2 4 {c8 c c c c4} c16 bf f8 \tuplet 3/2 8 {d16 e f g a bf} |
       
       c8. c16 c bf f8~ f4 r8 f16 g | a2.~ a16 bf c d |
       a16 a8.~ a4 r4 r16 c^\markup "cue" bf a |
       g2~ g8 f16 g \tuplet 3/2 {a16 bf b} c8 | g2~ g2 \fermata \bar "|."
   }
 >> 
 \layout {
   %indent = 0
 }
}