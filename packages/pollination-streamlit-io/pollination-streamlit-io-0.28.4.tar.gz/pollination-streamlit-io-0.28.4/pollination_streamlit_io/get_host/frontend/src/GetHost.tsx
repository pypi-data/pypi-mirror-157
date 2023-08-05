import React, { useEffect } from "react"

import { Streamlit } from "streamlit-component-lib"

import { getHost } from "pollination-react-io"

/**
 * GetGeometry renders a button that onClick returns an hbjson model from a CAD platform to Streamlit.
 * It also renders a checkbox that can be used subscribe to changes in the hbjson model from the CAD platform. 
 * 
 * in via renderData:
 * 
 * out via Streamlit.setComponentValue
 *   host: string 
 */
const GetHost: React.VFC = () => {

  useEffect(() => {
    Streamlit.setComponentValue(getHost())
  }, [])

  return (
    <></>
  )
}

export default GetHost
