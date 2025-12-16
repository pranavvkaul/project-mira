import React, { useState } from "react";
import { propertyData, getUniqueLocations } from "./data";
import Chatbot from "./Chatbot";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";
// --- Data Transformation Function ---
const buildLocationOptions = (data) => {
    // Used to count properties in the same city to create unique labels/values.
    const countMap = {};
    // Increment count for the current location if same location exists.
    return data.map((property) => {
        const baseLocation = property.location;

        countMap[baseLocation] = (countMap[baseLocation] || 0) + 1;

        const suffix = countMap[baseLocation];
        const label =
            countMap[baseLocation] > 1
                ? `${baseLocation} ${suffix}`
                : baseLocation;

        return {
            label,
            value: `${baseLocation}__${suffix}`,
            property,
        };
    });
};

const locationOptions = buildLocationOptions(propertyData);

// --- PropertyCard Sub-Component ---

const PropertyCard = ({ property, label }) => {
    if (!property) {
        return (
            <div className="flex-1 max-w-[600px] bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="p-5">
                    <h3 className="text-xl font-bold m-0">{label}</h3>
                    <p className="mt-2 text-gray-500">
                        Select a location above.
                    </p>
                </div>
            </div>
        );
    }

    const originalPrice = property.price;
    const predictedPrice = property.predicted_price;

    const formattedOriginal =
        typeof originalPrice === "number"
            ? originalPrice.toLocaleString("en-US", {
                  style: "currency",
                  currency: "USD",
                  maximumFractionDigits: 0,
              })
            : null;

    const formattedPredicted =
        typeof predictedPrice === "number"
            ? predictedPrice.toLocaleString("en-US", {
                  style: "currency",
                  currency: "USD",
                  maximumFractionDigits: 0,
              })
            : null;

    return (
        <div className="flex-1 max-w-[600px] bg-white rounded-lg shadow-lg overflow-hidden">
            <h3 className="px-6 py-4 text-2xl font-bold border-b">
                {property.title}
            </h3>

            <div className="w-full">
                <img
                    src={property.image_url}
                    alt={property.title}
                    className="w-full h-[280px] object-cover block"
                />
            </div>

            <div className="flex justify-between items-end px-6 py-4 border-b text-gray-900">
                <div className="flex flex-col items-start">
                    <div className="text-lg font-semibold">
                        Predicted: <strong>{formattedPredicted}</strong>
                    </div>
                    <div className="text-lg font-medium">
                        Original: {formattedOriginal}
                    </div>
                </div>

                <div className="flex flex-col items-end text-right">
                    <div className="flex items-center text-base font-medium mb-1">
                        <strong>{property.bedrooms}</strong>&nbsp;bds
                        <span className="mx-2 text-gray-300">|</span>
                        <strong>{property.bathrooms}</strong>&nbsp;ba
                        <span className="mx-2 text-gray-300">|</span>
                        <strong>
                            {property.size_sqft.toLocaleString()}
                        </strong>
                        &nbsp;sqft
                    </div>

                    <div className="text-lg font-bold">
                        {property.location}
                    </div>
                </div>
            </div>

            <div className="px-6 pt-4 pb-8">
                <ul className="flex flex-wrap gap-2 list-none p-0 m-0">
                    {property.amenities.map((amenity, index) => (
                        <li
                            key={index}
                            className="px-4 py-1.5 bg-gray-100 text-gray-800 rounded-md text-lg font-medium"
                        >
                            {amenity}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};
    // --- PropertyComparison Main Component ---
    const PropertyComparison = () => {
    const [location1, setLocation1] = useState(null);
    const [location2, setLocation2] = useState(null);

    const [comparisonProps, setComparisonProps] = useState({
        prop1: null,
        prop2: null,
    });

    // Handles the 'Compare' button click: sends data to the FastAPI backend for ML price prediction and updates the component state with results.

    const handleCompare = async () => {
        if (
            !location1 ||
            !location2 ||
            location1.value === location2.value
        ) {
            setComparisonProps({ prop1: null, prop2: null });
            return;
        }

        try {
                const res = await fetch(`${BACKEND_URL}/compare`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                address1: location1,
                address2: location2,
                })
,
            });

            if (res.ok) {
                const data = await res.json();

                const a = data.result?.address1 || null;
                const b = data.result?.address2 || null;

                const localA = location1.property;
                const localB = location2.property;

                const mergedA = a ? { ...localA, ...a } : localA;
                const mergedB = b ? { ...localB, ...b } : localB;

                setComparisonProps({
                    prop1: mergedA,
                    prop2: mergedB,
                });
            }
        } catch (err) {
            // Handle network errors or server failures
            console.warn(
                "Backend compare failed, falling back to local data",
                err
            );
        }
    };
    // --- Main Render Section ---

    return (
        <div className="min-h-screen">
            <header className="bg-white shadow-md px-12 py-5 flex items-center gap-10 h-[120px]">
                <h1 className="text-3xl font-extrabold text-gray-900 whitespace-nowrap">
                    Property Comparison & Price Prediction App
                </h1>

                <div className="flex items-center gap-5">
                    <select
                        className="bg-gray-100 border border-gray-300 rounded-md px-5 py-3 text-lg min-w-[200px]"
                        value={location1?.value || ""}
                        onChange={(e) => {
                            const selected = locationOptions.find(
                                (opt) => opt.value === e.target.value
                            );
                            setLocation1(selected);
                        }}
                    >
                        <option value="" disabled>
                            Select location
                        </option>
                        {locationOptions.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                                {opt.label}
                            </option>
                        ))}
                    </select>

                    <span className="text-lg font-semibold">vs</span>

                    <select
                        className="bg-gray-100 border border-gray-300 rounded-md px-5 py-3 text-lg min-w-[200px]"
                        value={location2?.value || ""}
                        onChange={(e) => {
                            const selected = locationOptions.find(
                                (opt) => opt.value === e.target.value
                            );
                            setLocation2(selected);
                        }}
                    >
                        <option value="" disabled>
                            Select location
                        </option>
                        {locationOptions.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                                {opt.label}
                            </option>
                        ))}
                    </select>

                    <button
                        className="px-8 py-3 bg-green-700 text-white rounded-md font-bold text-lg uppercase disabled:opacity-50"
                        onClick={handleCompare}
                        disabled={
                            !location1 ||
                            !location2 ||
                            location1 === location2
                        }
                    >
                        Compare
                    </button>

                    <Chatbot
                        prop1={comparisonProps?.prop1}
                        prop2={comparisonProps?.prop2}
                    />
                </div>
            </header>

            {comparisonProps && (
                <main className="flex justify-center gap-10 p-16 max-w-[1500px] mx-auto">
                    <PropertyCard
                        property={comparisonProps.prop1}
                        label="Property A"
                    />
                    <PropertyCard
                        property={comparisonProps.prop2}
                        label="Property B"
                    />
                </main>
            )}
        </div>
    );
};

export default PropertyComparison;
