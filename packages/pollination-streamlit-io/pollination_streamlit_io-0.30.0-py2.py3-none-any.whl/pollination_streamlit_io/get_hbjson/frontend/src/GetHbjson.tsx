import React, { useState, useEffect } from "react"

import { Streamlit } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"

import { GetModel } from "pollination-react-io"

const HEIGHT = 112

/**
 * GetHbjson renders a button that onClick returns an hbjson model from a CAD platform to Streamlit.
 * It also renders a checkbox that can be used subscribe to changes in the hbjson model from the CAD platform. 
 * 
 * in via renderData:
 * 
 * out via Streamlit.setComponentValue
 *   hbjson: dictionary
 *   host: string 
 */
 const GetHbjson: React.VFC = () => {
  // "useRenderData" returns the renderData passed from Python.
  const renderData = useRenderData()
  const theme = renderData.theme
  
  // TODO: this can be improved by varying height based on dropdown open state
  // Or even better by measuring height of button + dropdown and reporting height
  // from GetGeometryComponent in setParentState
  Streamlit.setFrameHeight(HEIGHT)

  const [state, setState] = useState()

  useEffect(() => {
    if(!state) return
    Streamlit.setComponentValue(state)
  }, [state])

  return (
    <div style={{
      height: HEIGHT,
      minHeight: HEIGHT,
      padding: 4
    }}>
    <GetModel setParentState={setState} />
    </div>
  )
}

export default GetHbjson