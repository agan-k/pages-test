---
title: "An Introduction to Modern Engraving"
date: "2026-07-07"
author: "Your Name"
summary: "Learning how to mix markdown text with high-quality LilyPond rendering."
---

Welcome to my blog! Here is a simple melody written inside a standard paragraph block:

<lilypond>
  \paper {
    page-breaking = #ly:one-page-breaking
    top-margin = 0
    bottom-margin = 0
    left-margin = 0
    right-margin = 0
    oddHeaderMarkup = ##f
    evenHeaderMarkup = ##f
    oddFooterMarkup = ##f
    evenFooterMarkup = ##f
  }
  \relative c' { c4 d e f | g1 }
</lilypond>

You can also pull in an entire separate score file from your assets directory like this:

<lilypond file="how-deep-is-the-ocean.ly" />

Happy writing!
