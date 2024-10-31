export const Hello = async (req, res) => {
    try {
        res.status(201).json({ message: 'Data collected successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

